
from audioop import reverse
from django.shortcuts import redirect, render
from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.contrib import messages
from authentication.models import User
from django_tables2 import RequestConfig
from django.db.models import Sum

from transactions.forms import BankTransactionAssignForm, TransactionCreateForm, TransactionUpdateForm, BankStatementImportForm
from transactions.models import BankTransaction, Transaction
from transactions.services import BankStatementParserService
from transactions.tables import BankTransactionTable, BankTransactionTableFilter,TransactionTable,TransactionTableFilter
# Create your views here.


class TransactionListView(LoginRequiredMixin, ListView):
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
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['filter']=filter
        context['table']=table
        context['total_credit'] = queryset.filter(type='credit').aggregate(Sum('amount'))['amount__sum']
        context['total_debit'] = queryset.filter(type='debit').aggregate(Sum('amount'))['amount__sum']

        return context
    

class TransactionCreateView(LoginRequiredMixin, CreateView):
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

class TransactionDetailView(LoginRequiredMixin, DetailView):
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


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
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
    


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    template_name ='transactions/delete.html'
    model = Transaction

    slug_field = 'id'
    slug_url_kwarg = 'id'

    success_url = reverse_lazy('transactions-list')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(created_by=self.request.user)
        else:
            return Transaction.objects.none()


class BankTransactionListView(LoginRequiredMixin, ListView):
    template_name ='transactions/bank_transaction_list.html'
    model = BankTransaction
    
    table_class = BankTransactionTable
    table_data = BankTransaction.objects.all()
    paginate_by = 5
    filterset_class = BankTransactionTableFilter
    context_filter_name = 'filter'

    def get_queryset(self, *args, **kwargs):
        qs = BankTransaction.objects.all()
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self,*args, **kwargs):
        context = super(BankTransactionListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = BankTransactionTableFilter(self.request.GET, queryset=queryset)
        table = BankTransactionTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['filter']=filter
        context['table']=table
        context['total_credit'] = queryset.filter(type='credit').aggregate(Sum('amount'))['amount__sum']
        context['total_debit'] = queryset.filter(type='debit').aggregate(Sum('amount'))['amount__sum']

        return context


class BankTransactionDetailView(LoginRequiredMixin, DetailView):
    template_name = 'transactions/bank_transaction_detail.html'
    model = Transaction
    context_object_name = 'bank_transaction'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return BankTransaction.objects.filter(created_by=self.request.user)
        else:
            return BankTransaction.objects.none()


class BankTransactionImportView(LoginRequiredMixin, View):
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
                print(message)
                messages.error(request, 'Error saving file data to database')
                return render(request, self.template_name,{'form':form})

            messages.success(request, 'Bank statement import successfull')
            return redirect('bank-transaction-list')

        messages.error(request, 'Something wrong with the input fields')
        return render(request, self.template_name,{'form':form})


class BankTransactionAssignView(LoginRequiredMixin, View):
    template_name = 'transactions/bank_transaction_assign.html'

    assign_scope = (
            ('shares', 'Shares'),
            ('savings', 'Saving'),
        )

    def get(self, request, uuid):
    
        context= context = self.get_context_data(uuid)

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

        return redirect('bank-transaction-list')

    
    def get_context_data(self, uuid):
        bank_trans= BankTransaction.objects.get(id=uuid)
        
        context= {
            'bank_transaction':bank_trans,
            'assign_scopes':self.assign_scope,
        }
        return context