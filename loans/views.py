
from multiprocessing import context
from re import template
from django.shortcuts import redirect, render, reverse
from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages

from django_tables2 import RequestConfig
from django.db.models import Sum

from loans.models import Loan, LoanRepayment
from loans.tables import LoanTable, LoanTableFilter
from authentication.models import Member, User
from loans.forms import LoanCreateFromBankTransactionForm, LoanRepaymentCreateForm, LoanRepaymentMemberSelectForm
from loans.services import LoanCreatorService
import loans.models as l_models
from transactions.models import BankTransaction

# Create your views here.
class LoanListView(LoginRequiredMixin, ListView):
    template_name ='loans/list.html'
    model = Loan
    
    table_class = LoanTable
    table_data = Loan.objects.all()
    filterset_class = LoanTableFilter
    context_filter_name = 'filter'

    def get_context_data(self,*args, **kwargs):
        context = super(LoanListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = LoanTableFilter(self.request.GET, queryset=queryset)
        table = LoanTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['filter']=filter
        context['table']=table
        context['loan_types']=l_models.LOAN_TYPE
        context['loan_status']=l_models.LOAN_STATUS
        context['total_principle'] = queryset.filter(status='issued').aggregate(Sum('principle'))['principle__sum']
        context['total_amount_issued'] = queryset.filter(status='issued').aggregate(Sum('amount_issued'))['amount_issued__sum']

        return context

class LoanCreateFromBankTransactionView(LoginRequiredMixin, View):
    template_name = 'loans/loan_create.html'

    def get(self, request, uuid):
        #Fetch bankTransaction
        
        bankTransaction = BankTransaction.objects.get(id=uuid)

        if bankTransaction is None:
            messages.error(request, 'Bank Transaction not found')
            return redirect('bank-transaction-list')
            
        context = self.get_context_data(uuid)

        return render(request, self.template_name, context)

    def post(self, request, uuid):

        form = LoanCreateFromBankTransactionForm(data= request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context)

        loancreateservice = LoanCreatorService()
        msg, created, loan = loancreateservice.create_loan_from_banktransaction(data=form.cleaned_data, creator=request.user)

        if not (created and loan is not None):
            messages.error(request, msg)
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context)

        return redirect(reverse('loan-detail', args=[loan.id]))

    def get_context_data(self, uuid):
        context={}
        context['banktransaction'] = BankTransaction.objects.get(id=uuid) 
        context['loan_types'] = l_models.LOAN_TYPE
        context['loan_statuses'] = l_models.LOAN_STATUS
        context['members'] = Member.objects.filter(is_active=True)
        return context
    



class LoanDetailView(LoginRequiredMixin, DetailView):
    template_name = 'loans/loan_detail.html'
    model = Loan
    context_object_name = 'loan'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):

        # if self.request.user.is_admin:
        #     return Loan.objects.filter(id=self.kwargs['id'])

        # if self.request.user.is_authenticated:
        #     return Loan.objects.filter( transaction__created_by=self.request.user)
        # else:
        #     return Loan.objects.none()

        return Loan.objects.filter(id=self.kwargs['id'])

class LoanRepaymentMemberSelectView(LoginRequiredMixin, View):
    template_name = 'loans/loanrepayment_select_member.html'
    model = LoanRepayment

    def get(self, request, uuid):
        bankTransaction = BankTransaction.objects.get(id=uuid)

        if bankTransaction is None:
            messages.error(request, 'Bank Transaction not found')
            return redirect('bank-transaction-list')
            
        context = self.get_context_data(uuid)
        context['banktransaction'] = bankTransaction

        return render(request, self.template_name, context)

    def post(self, request, uuid):

        form = LoanRepaymentMemberSelectForm(request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['banktransaction'] = BankTransaction.objects.get(id=uuid)
            context['form'] = form
            return render(request, self.template_name, context )
        
        return redirect(reverse('loanrepayment-select-loan', args=[uuid, form.cleaned_data['member']]))

    def get_context_data(self, uuid):
        context={}
        context['members'] = Member.objects.filter(is_active=True).only('id','first_name', 'last_name')
        return context


class LoanRepaymentCreateView(LoginRequiredMixin, View):
    template_name = 'loans/loanrepayment_create.html'
    model = LoanRepayment

    def get(self, request, transaction_id, member_id):
            
        context = self.get_context_data(transaction_id)
    
        return render(request, self.template_name, context)

    def post(self, request, uuid):

        form = LoanRepaymentCreateForm(request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context )

        #Create LoanRepaymentModel
        loancreateservice = LoanCreatorService()

        msg, created, loan = loancreateservice.create_loan_repaymet(form.cleaned_data, self.request.user)
        if not (created and loan is not None):
            messages.error(request, msg)
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context)
        
        return redirect(reverse('loanrepayment-list'))

    def get_context_data(self, transaction_id, member_id):
        context={}
        context['banktransaction'] = BankTransaction.objects.get(id=transaction_id).only('id')
        context['loans'] = Loan.objects.select_related('member').filter(member__id=member_id,member__is_active=True)
        return context
