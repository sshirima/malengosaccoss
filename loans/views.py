
from multiprocessing import context
from re import template
from django.shortcuts import redirect, render, reverse
from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from core.views.generic import BaseDetailView, BaseListView
from django_tables2 import RequestConfig
from django.db.models import Sum
import json
from django.http import JsonResponse

from loans.models import LOAN_TYPE, LOAN_STATUS, Loan, LoanRepayment
from loans.tables import LoanRepaymentDetailTable, LoanRepaymentTableExport, LoanTable, LoanTableExport, LoanTableFilter, LoanRepaymentTableFilter, LoanRepaymentTable
from authentication.models import User
from members.models import Member
from loans.forms import LoanCreateFromBankTransactionForm, LoanRepaymentCreateForm, LoanRepaymentMemberSelectForm
from loans.services import LoanCRUDService, LoanObject
import loans.models as l_models
from transactions.models import BankTransaction

# Create your views here.
class LoanListView(LoginRequiredMixin, BaseListView):

    template_name ='loans/loan_list.html'
    model = Loan
    table_class = LoanTable
    filterset_class = LoanTableFilter
    #Export options
    table_class_export = LoanTableExport
    export_filename = 'loans'


    def get_queryset(self, *args, **kwargs):
        filters = {}
        filters['member__user'] = self.request.user
        if self.request.user.is_staff:
            # qs = self.model.objects.filter(**kwargs)
            qs = self.model.objects.all()
        else:
            qs = self.model.objects.filter(**filters)

        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(LoanListView, self).get_context_data(queryset)
        context['loan_types']= LOAN_TYPE
        context['loan_status']= LOAN_STATUS
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

        loancreateservice = LoanCRUDService()
        msg, created, loan = loancreateservice.create_loan(data=form.cleaned_data, creator=request.user)

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
    
class LoanDetailView(LoginRequiredMixin, BaseDetailView):
    template_name = 'loans/loan_detail.html'
    model = Loan
    context_object_name = 'loan'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    paginate_by = 10

    def get_queryset(self):
        return super(LoanDetailView, self).get_queryset(id=self.kwargs['id'], member__user=self.request.user).select_related('transaction__reference','member__user')
        

    def get_context_data(self,*args, **kwargs):
        context = super(LoanDetailView, self).get_context_data()
        loan_object = LoanObject(loan=self.object)
        queryset = loan_object.loan_repayments
        self.set_loanrepayment_table(queryset, context)
        #Repayment and balance
        context['total_loanrepayment'] = loan_object.get_sum_loan_repayments()
        context['loan_balance'] = loan_object.get_outstanding_balance()
        
        return context

    def set_loanrepayment_table(self, queryset, context):
        filter = LoanRepaymentTableFilter(self.request.GET, queryset=queryset)
        table = LoanRepaymentDetailTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)
        context['filter']=filter
        context['table']=table

class LoanRepaymentListView(LoginRequiredMixin, BaseListView):

    template_name ='loans/loan_list.html'
    model = LoanRepayment
    table_class = LoanRepaymentTable
    filterset_class = LoanRepaymentTableFilter
    #Export options
    table_class_export = LoanTableExport
    export_filename = 'loanrepayment'

    #Export options
    table_class_export = LoanRepaymentTableExport
    export_filename = 'loanrepayments'

    def get_queryset(self, *args, **kwargs):
        filters = {}
        filters['loan__member__user'] = self.request.user
        return super(LoanRepaymentListView, self).get_queryset(**filters)

    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(LoanRepaymentListView, self).get_context_data(queryset)

        return context

class LoanRepaymentDetailView(LoginRequiredMixin, BaseDetailView):
    template_name = 'loans/loanrepayment_detail.html'
    model = LoanRepayment
    context_object_name = 'loanrepayment'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        return super(LoanRepaymentDetailView, self).get_queryset(id=self.kwargs['id'], member__user=self.request.user).select_related('transaction__reference','loan')
       

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
        
        return redirect(reverse('loanrepayment-create', args=[uuid, form.cleaned_data['member']]))

    def get_context_data(self, uuid):
        context={}
        context['members'] = Member.objects.filter(is_active=True).only('id','first_name', 'last_name')
        return context

class LoanRepaymentCreateView(LoginRequiredMixin, View):
    template_name = 'loans/loanrepayment_create.html'
    model = LoanRepayment

    def get(self, request, uuid1, uuid2):
            
        context = self.get_context_data(uuid1, uuid2)
    
        return render(request, self.template_name, context)

    def post(self, request, uuid1, uuid2):

        form = LoanRepaymentCreateForm(request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid1, uuid2)
            context['form'] = form
            return render(request, self.template_name, context )

        #Create LoanRepaymentModel
        loancreateservice = LoanCRUDService()

        msg, created, loan = loancreateservice.create_loan_repaymet(form.cleaned_data, self.request.user)
        if not (created and loan is not None):
            messages.error(request, msg)
            context = self.get_context_data(uuid1, uuid2)
            context['form'] = form
            return render(request, self.template_name, context)
        
        return redirect(reverse('loanrepayment-list'))

    def get_context_data(self, transaction_id, member_id):
        context={}
        context['banktransaction'] = transaction_id
        context['member'] = member_id
        context['loans'] = Loan.objects.select_related('member').filter(member__id=member_id,member__is_active=True)
        return context
