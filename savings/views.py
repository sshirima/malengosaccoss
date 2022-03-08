from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from authentication.models import User
from django_tables2 import RequestConfig
from django.db.models import Sum
from django.urls.base import reverse_lazy
from django.http import HttpResponseRedirect
from members.models import Member
from savings.forms import SavingCreateForm, SavingUpdateForm
from django.contrib import messages

from savings.models import Saving
from savings.tables import SavingTable, SavingTableFilter
from savings.services import SavingCRUDService
from transactions.models import BankTransaction
from authentication.permissions import BaseListView, BaseDetailView

# Create your views here.
class SavingListView(LoginRequiredMixin, BaseListView):
    template_name ='savings/saving-list.html'
    model = Saving
    table_class = SavingTable
    filterset_class = SavingTableFilter
    context_filter_name = 'filter'
    context_table_name = 'table'

    def get_queryset(self, *args, **kwargs):
        kwargs['owner__user'] = self.request.user
        return super(SavingListView, self).get_queryset(**kwargs)

    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(SavingListView, self).get_context_data(queryset)
        context['total_saving'] = queryset.aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        return context


class SavingCreateView(LoginRequiredMixin, CreateView):
    template_name ='savings/saving_create.html'
    form_class = SavingCreateForm
    context_object_name = 'saving'
    success_url = reverse_lazy('savings-list')

    def get(self, request, uuid):
        context = self.get_context_data(uuid)
        return render(request, self.template_name, context)


    def post(self, request, uuid):
        form = SavingCreateForm(uuid=uuid,data= request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        service = SavingCRUDService()
        data = form.cleaned_data
        data['uuid'] = uuid
        msg, created, share = service.create_saving(data=data, created_by=self.request.user)

        if not created and share is None:
            messages.error(self.request, msg)
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        messages.success(self.request, 'Saving record added successful')
        return HttpResponseRedirect(share.get_absolute_url())

    def get_context_data(self,uuid):
        context = {}
        context['owners'] = Member.objects.all()
        context['bank_transaction'] = BankTransaction.objects.get(id=uuid)
        return context


class SavingDetailView(LoginRequiredMixin, BaseDetailView):
    template_name = 'savings/saving_detail.html'
    model = Saving
    context_object_name = 'saving'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        return super(SavingDetailView, self).get_queryset(id=self.kwargs['id'], owner__user=self.request.user)


class SavingUpdateView(LoginRequiredMixin, UpdateView):
    template_name ='savings/saving_update.html'
    model = Saving
    context_object_name = 'saving'
    form_class = SavingUpdateForm
    success_url = reverse_lazy('shares-list')
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def form_valid(self, form):
       
        #Create transaction first

        saving = Saving.objects.get(id=self.kwargs['id'])

        if not saving:
            return super.form_invalid()

        saving.description = form.cleaned_data['description']
        saving.save()
        
        return HttpResponseRedirect(saving.get_absolute_url())

        

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Saving.objects.filter(transaction__created_by=self.request.user)
        else:
            return Saving.objects.none()

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(SavingUpdateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs




class SavingDeleteView(LoginRequiredMixin, DeleteView):
    template_name ='savings/saving_delete.html'
    model = Saving

    slug_field = 'id'
    slug_url_kwarg = 'id'

    success_url = reverse_lazy('savings-list')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Saving.objects.filter(id=self.kwargs['id'])
        else:
            return Saving.objects.none()


    def form_valid(self, form):
        self.object = self.get_object()
        service = SavingCRUDService()
        msg, deleted, trans = service.delete_saving(self.object)

        if deleted:
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)

        messages.error(self.request, msg)
        return HttpResponseRedirect(reverse_lazy('savings-list'))
        