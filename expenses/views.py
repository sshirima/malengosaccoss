from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from authentication.models import User
from django_tables2 import RequestConfig
from django.db.models import Sum
from django.urls.base import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages

from expenses.forms import ExpenseCreateForm, ExpenseUpdateForm
from expenses.models import Expense
from expenses.tables import ExpenseTable, ExpenseTableFilter
from expenses.services import ExpenseCrudService
from members.models import Member
from transactions.models import BankTransaction
from authentication.permissions import BaseUserPassesTestMixin

# Create your views here.
class ExpenseListView(LoginRequiredMixin,BaseUserPassesTestMixin, ListView):
    template_name ='expenses/expense-list.html'
    model = Expense
    
    table_class = ExpenseTable
    table_data = Expense.objects.all()
    filterset_class = ExpenseTableFilter
    context_filter_name = 'filter'

    def get_queryset(self, *args, **kwargs):
        qs = Expense.objects.filter(transaction__created_by = self.request.user)
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self,*args, **kwargs):
        context = super(ExpenseListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = ExpenseTableFilter(self.request.GET, queryset=queryset)
        table = ExpenseTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['filter']=filter
        context['table']=table
        context['total_amount'] = queryset.aggregate(Sum('transaction__amount'))['transaction__amount__sum']

        return context


class ExpenseCreateView(LoginRequiredMixin,BaseUserPassesTestMixin, CreateView):
    template_name ='expenses/expense_create.html'
    form_class = ExpenseCreateForm
    context_object_name = 'expense'
    success_url = reverse_lazy('expense-list')

    def get(self, request, uuid):
        context = self.get_context_data(uuid)
        return render(request, self.template_name, context)


    def post(self, request, uuid):
        form = ExpenseCreateForm(uuid=uuid,data= request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        service = ExpenseCrudService(self.request)
        data = form.cleaned_data
        data['uuid'] = uuid
        msg, created, share = service.create_expense(data=data, created_by=self.request.user)

        if not created and share is None:
            messages.error(self.request, msg)
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        messages.success(self.request, 'Expense record added successful')
        return HttpResponseRedirect(share.get_absolute_url())

    def get_context_data(self,uuid):
        context = {}
        context['owners'] = Member.objects.all()
        context['bank_transaction'] = BankTransaction.objects.get(id=uuid)
        return context


class ExpenseCreateMultipleView(LoginRequiredMixin,BaseUserPassesTestMixin, View):
    template_name ='expenses/expense_create_multiple.html'
    form_class = ExpenseCreateForm
    success_url = reverse_lazy('expense-list')

    def get(self, request, uuid):
        context = self.get_context_data(uuid)
        return render(request, self.template_name, context)


    def post(self, request, uuid):
        form = ExpenseCreateForm(uuid=uuid,data= request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        service = ExpenseCrudService(self.request)
        data = form.cleaned_data
        data['uuid'] = uuid
        msg, created, expense = service.create_expense(data=data, created_by=self.request.user)

        if not created and expense is None:
            messages.error(self.request, msg)
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        messages.success(self.request, 'Expense record added successful')
        return HttpResponseRedirect(expense.get_absolute_url())

    def get_context_data(self,uuid):
        context = {}
        context['owners'] = Member.objects.all()
        context['bank_transaction'] = BankTransaction.objects.get(id=uuid)
        return context


class ExpenseDetailView(LoginRequiredMixin,BaseUserPassesTestMixin, DetailView):
    template_name = 'expenses/expense_detail.html'
    model = Expense
    context_object_name = 'expense'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):

        if self.request.user.is_admin:
            return Expense.objects.filter(id=self.kwargs['id'])

        if self.request.user.is_authenticated:
            return Expense.objects.filter( transaction__created_by=self.request.user)
        else:
            return Expense.objects.none()


class ExpenseUpdateView(LoginRequiredMixin,BaseUserPassesTestMixin, UpdateView):
    template_name ='expenses/expense_update.html'
    model = Expense
    context_object_name = 'expense'
    form_class = ExpenseUpdateForm
    success_url = reverse_lazy('shares-list')
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def form_valid(self, form):
       
        #Create transaction first

        expense = Expense.objects.get(id=self.kwargs['id'])

        if not expense:
            return super.form_invalid()

        expense.description = form.cleaned_data['description']
        expense.save()
        
        return HttpResponseRedirect(expense.get_absolute_url())

        

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Expense.objects.filter(transaction__created_by=self.request.user)
        else:
            return Expense.objects.none()

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ExpenseUpdateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class ExpenseDeleteView(LoginRequiredMixin,BaseUserPassesTestMixin, DeleteView):
    template_name ='expenses/expense_delete.html'
    model = Expense

    slug_field = 'id'
    slug_url_kwarg = 'id'

    success_url = reverse_lazy('expenses-list')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Expense.objects.filter(id=self.kwargs['id'])
        else:
            return Expense.objects.none()


    def form_valid(self, form):
        self.object = self.get_object()
        service = ExpenseCrudService(self.request)
        msg, deleted, trans = service.delete_expense(self.object)

        if deleted:
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)

        messages.error(self.request, msg)
        return HttpResponseRedirect(reverse_lazy('expenses-list'))
        