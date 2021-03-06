
from datetime import datetime
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport
from django.db.models import Sum
from members.models import Member
import json
from django.http import JsonResponse
from core.utils import get_timestamps_filename


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
from transactions.models import (
    BANK_TRANSACTION_STATUS,
    TRANSACTION_STATUS,
    TRANSACTION_TYPE,
    BankStatement,
    get_transaction_assignment_action_by_type, 
    get_transaction_assignment_action_all,
    BankTransaction, 
    Transaction,
)
import transactions.models as tr_models
from loans.models import Loan, LOAN_TYPE
from transactions.services import BankStatementParserService, BankTransactionAssignmentService, TransactionCRUDService
from transactions.tables import (
    BankStatementTable,
    BankStatementTransactionsTable,
    BankTransactionFlatTable, 
    BankTransactionTable,
    BankTransactionTableExport, 
    BankTransactionTableFilter,
    TransactionTable,
    TransactionTableExport,
    TransactionTableFilter
)
from authentication.permissions import MemberStaffPassTestMixin
from core.views.generic import BaseListView
# Create your views here.

def get_member_loans(request):

    if request.method == "POST":
        if request.user.is_authenticated:
            member_id = json.loads(request.body).get('owner_id')
            loans = Loan.objects.filter(member__id = member_id).values('id','principle', 'type')
            return JsonResponse(list(loans), safe=False)
            
        return JsonResponse(list({}), safe=False)           

class TransactionListView(LoginRequiredMixin,MemberStaffPassTestMixin, BaseListView):
    
    template_name ='transactions/list.html'
    model = Transaction
    table_class = TransactionTable
    filterset_class = TransactionTableFilter
    
    #Export options
    table_class_export = TransactionTableExport
    export_filename = None


    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(TransactionListView, self).get_context_data(queryset)
        context['transaction_types']=TRANSACTION_TYPE
        context['transaction_statuses']=TRANSACTION_STATUS

        return context
    
class TransactionCreateView(LoginRequiredMixin,MemberStaffPassTestMixin, CreateView):
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

class TransactionDetailView(LoginRequiredMixin,MemberStaffPassTestMixin, DetailView):
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

class TransactionUpdateView(LoginRequiredMixin,MemberStaffPassTestMixin, UpdateView):
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
    
class TransactionDeleteView(LoginRequiredMixin,MemberStaffPassTestMixin, DeleteView):
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

class BankTransactionListView(LoginRequiredMixin,MemberStaffPassTestMixin, BaseListView):
    template_name ='transactions/bank_transaction_list.html'
    model = BankTransaction
    table_class = BankTransactionTable
    filterset_class = BankTransactionTableFilter

    #Export options
    table_class_export = BankTransactionTableExport
    export_filename = None

    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(BankTransactionListView, self).get_context_data(queryset)
        context['transaction_types']=TRANSACTION_TYPE
        context['transaction_statuses']=BANK_TRANSACTION_STATUS
        type_get = self.request.GET.get('type')
        context['table_actions'] = get_transaction_assignment_action_by_type(type_get, as_items=True) if type_get else get_transaction_assignment_action_all(as_items=True)
        
        return context

class BankTransactionDetailView(LoginRequiredMixin,MemberStaffPassTestMixin, DetailView):
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

class BankTransactionImportView(LoginRequiredMixin,MemberStaffPassTestMixin, View):
    template_name = 'transactions/bank_transaction_import.html'

    def get(self, request):
        form = BankStatementImportForm()
        return render(request, self.template_name,{'form':form})

    def post(self, request):
        form = BankStatementImportForm(request.POST, request.FILES)
        parserService = BankStatementParserService()
        
        if form.is_valid():
            uploaded_file = form.cleaned_data['import_file']
            import_file_path = uploaded_file.temporary_file_path()
            file_name = get_timestamps_filename(datetime.now(), uploaded_file.name)
            # print(file_name)

            column_names = ['Tran Date', 'Value Date','Tran Particulars','Instrument\nId','Debit','Credit', 'Balance']
            df = parserService.parse_xlsx_file(filename=import_file_path, column_names=column_names)
            
            if len(df.index) == 0:
                messages.error(request, 'File contain no transaction information')
                return render(request, self.template_name,{'form':form})

            message, created, qs = parserService.create_bank_transaction_db(df, column_names, self.request.user, filename=file_name)
            
            if not created:
                messages.error(request, message)
                return render(request, self.template_name,{'form':form})

            messages.success(request, 'Bank statement import successfull')
            return redirect('bank-transaction-list')

        messages.error(request, 'Something wrong with the input fields')
        return render(request, self.template_name,{'form':form})

class BankTransactionAssignView(LoginRequiredMixin,MemberStaffPassTestMixin, View):
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

class BankTransactionMultipleAssignView(LoginRequiredMixin,MemberStaffPassTestMixin, View):
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

class BankTransactionMultipleAssignConfirmView(LoginRequiredMixin,MemberStaffPassTestMixin, View):

    def post(self, request):

        is_valid, form = self.get_validated_form(request)

        if not is_valid:

            if form is not None:
                form.get_error_messages_from_form(request, form)

            return redirect('bank-transaction-list')

        service = BankTransactionAssignmentService()
        kwargs = form.cleaned_data
        kwargs['created_by'] = request.user
        print(kwargs)

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
                'description':request.POST['description'],
                'amount':request.POST['amount'],
            })

            return form.is_valid(), form

        elif action == 'assign_to_savings':

            form = BankTransactionMultipleAssignSavingForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
                'description':request.POST['description'],
                'amount':request.POST['amount'],
            })

            return form.is_valid(), form

        elif action == 'assign_to_loanrepayments':

            form = BankTransactionMultipleAssignLoanRepaymentForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
                'loan':request.POST['loan'],
                'description':request.POST['description'],
                'amount':request.POST['amount'],
            })

            return form.is_valid(), form
            
        elif action == 'assign_to_loans':

            form = BankTransactionMultipleAssignLoanForm({
                'action':action,
                'selection':','.join(selections),
                'owner':request.POST['owner'],
                'duration':request.POST['duration'],
                'loan_type':request.POST['loan_type'],
                'description':request.POST['description'],
                'amount':request.POST['amount'],
            })

            return form.is_valid(), form

        elif action == 'assign_to_expenses':

            form = BankTransactionMultipleAssignExpenseForm({
                'action':action,
                'selection':','.join(selections),
                'description':request.POST['description'],
                'amount':request.POST['amount'],
            })
            return form.is_valid(), form
        else:
            messages.error(request, 'Not a valid action')
            return False, None

class BankStatementListView(LoginRequiredMixin,MemberStaffPassTestMixin, BaseListView):
    template_name ='transactions/bankstatement_list.html'
    model = BankStatement
    table_class = BankStatementTable
    filterset_class = None
    
    #Export options
    table_class_export = TransactionTableExport
    export_filename = None


    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(BankStatementListView, self).get_context_data(queryset)
        return context

class BankStatementDetailView(LoginRequiredMixin,MemberStaffPassTestMixin, DetailView):
    template_name = 'transactions/bankstatement_detail.html'
    model = BankStatement
    context_object_name = 'bankstatement'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    paginate_by = 10

    def get_queryset(self):
        return BankStatement.objects.select_related('created_by').filter(id = self.kwargs['id'])

    def get_context_data(self,*args, **kwargs):
        context = super(BankStatementDetailView, self).get_context_data(**kwargs)
        bankstransactions = BankTransaction.objects.filter(bankstatement=self.object )
        table = BankStatementTransactionsTable(bankstransactions)
        RequestConfig(self.request, paginate={"per_page": self.paginate_by}).configure(table)  
        context['table'] = table
        return context

class BankStatementDeleteView(LoginRequiredMixin,MemberStaffPassTestMixin, DeleteView):
    template_name ='transactions/bankstatement_delete.html'
    model = BankStatement
    slug_field = 'id'
    slug_url_kwarg = 'id'

    success_url = reverse_lazy('bank-statement-list')

    def get_queryset(self):
        return BankStatement.objects.filter(id=self.kwargs['id'])

    def get_context_data(self, **kwargs):
        context = super(BankStatementDeleteView, self).get_context_data()
        # print(related_objects)
        context['banktransactions'] = BankTransaction.objects.filter(bankstatement = self.object)
        return context

    

    def form_valid(self, form):
        self.object = self.get_object()
        service = BankStatementParserService()
        deleted= service.delete_bankstatement_object(self.object)

        if deleted:
            messages.success(self.request, 'Bank statement deleted successful')
            return HttpResponseRedirect(self.get_success_url())

        messages.error(self.request, 'Fails to delete bank statement')
        return HttpResponseRedirect(reverse_lazy('bank-statement-list'))