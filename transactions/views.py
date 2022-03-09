
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_tables2 import RequestConfig
from django.db.models import Sum
from members.models import Member
import json
from django.http import JsonResponse

from transactions.forms import (
    BankTransactionAssignForm,
    BankTransactionMultipleAssignExpenseForm, 
    BankTransactionMultipleAssignForm,
    BankTransactionMultipleAssignLoanForm,
    BankTransactionMultipleAssignLoanRepaymentForm,
    BankTransactionMultipleAssignSavingForm, 
    BankTransactionMultipleAssignShareForm, 
    TransactionCreateForm, 
    TransactionUpdateForm, 
    BankStatementImportForm
)
from transactions.models import BankTransaction, Transaction
import transactions.models as tr_models
from loans.models import Loan, LOAN_TYPE
from transactions.services import BankStatementParserService, BankTransactionAssignmentService, TransactionCRUDService
from transactions.tables import (
    BankTransactionFlatTable, 
    BankTransactionTable, 
    BankTransactionTableFilter,
    TransactionTable,
    TransactionTableFilter
)
from authentication.permissions import BaseUserPassesTestMixin
from authentication.permissions import BaseListView
# Create your views here.


class TransactionListView(LoginRequiredMixin,BaseUserPassesTestMixin, ListView):
    template_name ='transactions/list.html'
    model = Transaction
    
    table_class = TransactionTable
    table_data = Transaction.objects.all()
    paginate_by = 5
    filterset_class = TransactionTableFilter
    context_filter_name = 'filter'

    def get_context_data(self,*args, **kwargs):
        context = super(TransactionListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = TransactionTableFilter(self.request.GET, queryset=queryset)
        table = TransactionTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['filter']=filter
        context['table']=table
        context['total_credit'] = queryset.filter(type='credit').aggregate(Sum('amount'))['amount__sum']
        context['total_debit'] = queryset.filter(type='debit').aggregate(Sum('amount'))['amount__sum']

        return context
    

class TransactionCreateView(LoginRequiredMixin,BaseUserPassesTestMixin, CreateView):
    template_name ='transactions/create.html'
    form_class = TransactionCreateForm
    context_object_name = 'transaction'


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(TransactionCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class TransactionDetailView(LoginRequiredMixin,BaseUserPassesTestMixin, DetailView):
    template_name = 'transactions/detail.html'
    model = Transaction
    context_object_name = 'transaction'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(created_by=self.request.user)
        else:
            return Transaction.objects.none()


class TransactionUpdateView(LoginRequiredMixin,BaseUserPassesTestMixin, UpdateView):
    template_name ='transactions/update.html'
    model = Transaction
    context_object_name = 'transaction'
    form_class = TransactionUpdateForm
    success_url = reverse_lazy('transactions-list')
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(created_by=self.request.user)
        else:
            return Transaction.objects.none()

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(TransactionUpdateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs
    

class TransactionDeleteView(LoginRequiredMixin,BaseUserPassesTestMixin, DeleteView):
    template_name ='transactions/delete.html'
    model = Transaction
    slug_field = 'id'
    slug_url_kwarg = 'id'

    success_url = reverse_lazy('transactions-list')

    def get_queryset(self):
        return Transaction.objects.filter(id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(TransactionDeleteView, self).get_context_data()

        transaction = Transaction.objects.get(id = self.kwargs['id'])
        
        context['related_objects'] = self.get_related_models(transaction)
        return context

    def get_related_models(self, object):
        related_list = object.get_ralated_list()
        related_objects = []
        if related_list:
            for related in related_list:
                for m in related:
                    name = m._meta.verbose_name + " ("+str(m)+")"
                    related_objects.append({'name':name, 'url': m.get_absolute_url()})

        return related_objects

    def form_valid(self, form):
        self.object = self.get_object()
        service = TransactionCRUDService()
        msg, deleted, trans = service.delete_transaction(self.object)

        if deleted:
            messages.success(self.request, 'Transaction deleted successfull')
            return HttpResponseRedirect(self.get_success_url())

        messages.error(self.request, msg)
        return HttpResponseRedirect(reverse_lazy('transactions-list'))


class BankTransactionListView(LoginRequiredMixin,BaseUserPassesTestMixin, ListView):
    template_name ='transactions/bank_transaction_list.html'
    filterset_class = BankTransactionTableFilter

    def get_queryset(self, *args, **kwargs):
        qs = BankTransaction.objects.all()
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self,*args, **kwargs):
        context = super(BankTransactionListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = BankTransactionTableFilter(self.request.GET, queryset=queryset)
        table = BankTransactionTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 20}).configure(table)
        context['filter']=filter
        context['table']=table
        context['transaction_types']=tr_models.TRANSACTION_TYPE
        context['transaction_statuses']=tr_models.BANK_TRANSACTION_STATUS

        if not self.request.GET.get('type') :
            context['table_actions'] = tr_models.get_transaction_assignment_action_all(as_items=True)
        else:
            context['table_actions'] = tr_models.get_transaction_assignment_action_by_type(self.request.GET.get('type'), as_items=True)

        context['total_credit'] = queryset.filter(type='credit').aggregate(Sum('amount'))['amount__sum']
        context['total_debit'] = queryset.filter(type='debit').aggregate(Sum('amount'))['amount__sum']

        return context


class BankTransactionDetailView(LoginRequiredMixin,BaseUserPassesTestMixin, DetailView):
    template_name = 'transactions/bank_transaction_detail.html'
    model = Transaction
    context_object_name = 'bank_transaction'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        # if self.request.user.is_authenticated:
        #     return BankTransaction.objects.filter(created_by=self.request.user)
        # else:
        #     return BankTransaction.objects.none()
        return BankTransaction.objects.filter(id = self.kwargs['id'])


class BankTransactionImportView(LoginRequiredMixin,BaseUserPassesTestMixin, View):
    template_name = 'transactions/bank_transaction_import.html'

    def get(self, request):
        form = BankStatementImportForm()
        return render(request, self.template_name,{'form':form})

    def post(self, request):
        form = BankStatementImportForm(request.POST, request.FILES)
        parserService = BankStatementParserService()
        
        if form.is_valid():
            import_file_path = form.cleaned_data['import_file'].temporary_file_path()

            column_names = ['Tran Date', 'Value Date','Tran Particulars','Instrument\nId','Debit','Credit', 'Balance']
            df = parserService.parse_xlsx_file(filename=import_file_path, column_names=column_names)
            
            if len(df.index) == 0:
                messages.error(request, 'Error, parsing the file')
                return render(request, self.template_name,{'form':form})

            message, created, qs = parserService.create_bank_transaction_db(df, column_names, self.request.user)
            
            if not created:
                messages.error(request, message)
                return render(request, self.template_name,{'form':form})

            messages.success(request, 'Bank statement import successfull')
            return redirect('bank-transaction-list')

        messages.error(request, 'Something wrong with the input fields')
        return render(request, self.template_name,{'form':form})


class BankTransactionAssignView(LoginRequiredMixin,BaseUserPassesTestMixin, View):
    template_name = 'transactions/bank_transaction_assign.html'

    assign_scope = (
                ('shares', 'Shares'),
                ('savings', 'Saving'),
                ('expenses', 'Expenses'),
                ('loans', 'Loans'),
                ('loanrepayment', 'Loan Repayments'),
            )

    def get(self, request, uuid):
    
        context = self.get_context_data(uuid)

        return render(request, self.template_name, context)
    

    def post(self, request, uuid):
        form = BankTransactionAssignForm(uuid=uuid, data=request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form']= form
            return render(request, self.template_name, context)


        if form.cleaned_data['assign_scope'] == self.assign_scope[0][0]:
            return redirect('share-create', uuid=uuid)

        if form.cleaned_data['assign_scope'] == self.assign_scope[1][0]:
            return redirect('saving-create', uuid=uuid)

        if form.cleaned_data['assign_scope'] == self.assign_scope[2][0]:
            return redirect('expense-create', uuid=uuid)

        if form.cleaned_data['assign_scope'] == self.assign_scope[3][0]:
            return redirect('loan-create', uuid=uuid)

        if form.cleaned_data['assign_scope'] == self.assign_scope[4][0]:
            return redirect('loanrepayment-select-member', uuid=uuid)

        messages.error(request, 'Could not action the assignment')
        return redirect('bank-transaction-list')

    
    def get_context_data(self, uuid):
        bank_trans= BankTransaction.objects.get(id=uuid)

        if bank_trans.type == tr_models.TRANSACTION_TYPE[0][0]:
            assign_scope = (
                ('expenses', 'Expenses'),
                ('loans', 'Loans'),
            )
        else:
            assign_scope = (
                ('shares', 'Shares'),
                ('savings', 'Saving'),
                ('loanrepayment', 'Loan Repayements'),
            )
        
        context= {
            'bank_transaction':bank_trans,
            'assign_scopes':assign_scope,
        }
        return context


class BankTransactionMultipleAssignView(LoginRequiredMixin,BaseUserPassesTestMixin, View):
    template_name = 'transactions/bank_transaction_assign_multiple.html'
    model = BankTransaction
    table_class = BankTransactionFlatTable
    context_table_name = 'table'
    paginate_by = 10

    def post(self, request):
        action = request.POST.get('action')
        selections = request.POST.getlist('selection')
        form = BankTransactionMultipleAssignForm({
            'action':action,
            'selection':','.join(selections)
        })

        if not form.is_valid():
            form.get_error_messages_from_form(request, form)
            return redirect('bank-transaction-list')

        context = self.get_context_data(action=form.cleaned_data['action'], selections=form.cleaned_data['selection'])

        return render(request, self.template_name, context)

    def get_context_data(self, *args, **kwargs):
        #Get Table
        context = {}
        queryset = self.get_queryset(selections=kwargs['selections'])
        table = self.table_class(queryset)
        context[self.context_table_name]=table
        context['action']= tr_models.get_transaction_assignment_action_by_key(kwargs['action'])

        if kwargs['action'] in ['assign_to_shares', 'assign_to_savings', 'assign_to_loanrepayments', 'assign_to_loans']:
            context['owners'] = Member.objects.all().only('id','first_name','middle_name','last_name')

        if kwargs['action'] == 'assign_to_loans':
            context['loan_types'] = LOAN_TYPE

        return context

    def get_queryset(self, *args, **kwargs):
        self.object_list = BankTransaction.objects.filter(id__in=kwargs['selections'])
        return self.object_list


class BankTransactionMultipleAssignConfirmView(LoginRequiredMixin,BaseUserPassesTestMixin, View):

    def post(self, request):

        is_valid, form = self.get_validated_form(request)

        if not is_valid:

            if form is not None:
                form.get_error_messages_from_form(request, form)

            return redirect('bank-transaction-list')

        service = BankTransactionAssignmentService()
        kwargs = form.cleaned_data
        kwargs['created_by'] = request.user

        results= service.assign_banktransactions_with_action(
            form.cleaned_data['selection'],
            **kwargs
        )

        for result in results:
            if not result['created']:
                messages.error(request, result['msg'])
            else:
                messages.success(request, 'Transaction assigned successfull: {}'.format(result['object']))
        
        return redirect('bank-transaction-list')

    def get_validated_form(self, request):

        action = request.POST.get('action')
        selections = request.POST.getlist('selection')
        
        if action == 'assign_to_shares':

            form = BankTransactionMultipleAssignShareForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
            })

            return form.is_valid(), form

        elif action == 'assign_to_savings':

            form = BankTransactionMultipleAssignSavingForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
            })

            return form.is_valid(), form

        elif action == 'assign_to_loanrepayments':

            form = BankTransactionMultipleAssignLoanRepaymentForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
                'loan':request.POST['loan'],
            })

            return form.is_valid(), form
            
        elif action == 'assign_to_loans':

            form = BankTransactionMultipleAssignLoanForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
                'duration':request.POST['duration'],
                'loan_type':request.POST['loan_type'],
            })

            return form.is_valid(), form

        elif action == 'assign_to_expenses':

            form = BankTransactionMultipleAssignExpenseForm({
                'action':action,
                'selection':','.join(selections),
            })
            return form.is_valid(), form
        else:
            messages.error(request, 'Not a valid action')
            return False, None

def get_member_loans(request):

    if request.method == "POST":
        if request.user.is_authenticated:
            member_id = json.loads(request.body).get('owner_id')
            loans = Loan.objects.filter(member__id = member_id).values('id','principle', 'type')
            return JsonResponse(list(loans), safe=False)
            
        return JsonResponse(list({}), safe=False)           