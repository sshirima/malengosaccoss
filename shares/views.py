

from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django_tables2 import RequestConfig
from django.shortcuts import render
from django.contrib import messages
from members.models import Member
import shares.models as share_models
from shares.services import ShareCrudService

from transactions.models import BankTransaction, Transaction
from authentication.models import User
from django.db.models import Sum

from .forms import ShareCreateForm, ShareUpdateForm, ShareAuthorizationForm
from .models import Share
from .tables import ShareTable, ShareTableFilter
from authentication.permissions import BaseListView, BaseDetailView, BaseUpdateView
# Create your views here.


class ShareListView(LoginRequiredMixin, BaseListView):
    template_name ='shares/list.html'
    model = Share
    table_class = ShareTable
    filterset_class = ShareTableFilter
    context_filter_name = 'filter'
    context_table_name = 'table'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        kwargs['owner__user'] = self.request.user
        return super(ShareListView, self).get_queryset(**kwargs)

    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(ShareListView, self).get_context_data(queryset)
        context['total_share'] = queryset.aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        return context
    

class ShareCreateView(LoginRequiredMixin, CreateView):
    template_name ='shares/create.html'
    form_class = ShareCreateForm
    context_object_name = 'share'
    success_url = reverse_lazy('share-list')

    def get(self, request, uuid):
        context = self.get_context_data(uuid)
        return render(request, self.template_name, context)


    def post(self, request, uuid):
        form = ShareCreateForm(uuid=uuid,data= request.POST)

        if not form.is_valid():
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        service = ShareCrudService()
        data = form.cleaned_data
        data['uuid'] = uuid
        msg, created, share = service.create_share(data=data, created_by=self.request.user)

        if not created and share is None:
            messages.error(self.request, msg)
            context = self.get_context_data(uuid)
            context['form'] = form
            return render(request, self.template_name, context) 

        messages.success(self.request, 'Share created successful')
        return HttpResponseRedirect(share.get_absolute_url())

    def get_context_data(self,uuid):
        context = {}
        context['owners'] = Member.objects.all()
        context['bank_transaction'] = BankTransaction.objects.get(id=uuid)
        return context
        

class ShareDetailView(LoginRequiredMixin, BaseDetailView):
    template_name = 'shares/detail.html'
    model = Share
    context_object_name = 'share'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        return super(ShareDetailView, self).get_queryset(id=self.kwargs['id'], owner__user=self.request.user)
        


class ShareUpdateView(LoginRequiredMixin, BaseUpdateView):
    template_name ='shares/update.html'
    model = Share
    context_object_name = 'share'
    form_class = ShareUpdateForm
    success_url = reverse_lazy('shares-list')
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        return super(ShareUpdateView, self).get_queryset(id=self.kwargs['id'], owner__user=self.request.user)


    def form_valid(self, form):
       
        #Create transaction first
        sharecrudservice = ShareCrudService()
        data_kwargs = form.cleaned_data
        data_kwargs['id'] = self.kwargs['id']

        msg, updated, share = sharecrudservice.update_share(**data_kwargs)
        
        if not updated and share is None:
            messages.error(self.request, msg)
            return super.form_invalid()

        return HttpResponseRedirect(share.get_absolute_url())

        

    

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ShareUpdateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs
    


class ShareDeleteView(LoginRequiredMixin, DeleteView):
    template_name ='shares/delete.html'
    model = Share

    slug_field = 'id'
    slug_url_kwarg = 'id'

    success_url = reverse_lazy('shares-list')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Share.objects.filter(id=self.kwargs['id'])
        else:
            return Share.objects.none()

    def form_valid(self, form):
        self.object = self.get_object()
        service = ShareCrudService()
        msg, deleted, trans = service.delete_share(self.object)

        if deleted:
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)

        messages.error(self.request, msg)
        return HttpResponseRedirect(reverse_lazy('shares-list'))


class ShareAuthorizeView(LoginRequiredMixin, View):
    template_name = 'shares/authorize.html'

    def get(self, request, uuid):
        context = {
            'uuid':uuid
        }
        try:
            share = Share.objects.get(id=uuid)
            context['share'] = share
            context['status_list'] = share_models.SHARE_STATUS

        except Share.DoesNotExist as e:
            messages.error(request, 'Share not found, id:'+uuid)
            print('ERROR, share does not exist: {}'.format(str(e)))

        return render(request, self.template_name, context)


    def post(self, request, uuid):
        form = ShareAuthorizationForm(request.POST)
        context = {
            'form': form, 
            'uuid':uuid
        }
        if form.is_valid():
            status = form.cleaned_data['status']

            share = Share.objects.get(id=uuid)

            if not request.user.is_admin:
                messages.error(request, 'You dont have permission to authorize shares')
                return render(request, self.template_name, context)

            if not share:
                messages.error(request, 'Record does not exist: '+uuid)
                return render(request, self.template_name, context)

            if share.status == 'cancelled':
                messages.error(request, 'Share in unauthorized state: '+share.status)
                return redirect(reverse('share-detail', args=[uuid]))

            if share.status == 'approved':
                messages.error(request, 'Share is in approved state: '+share.status)
                return redirect(reverse('share-detail', args=[uuid]))

            if share.status =='pending' and status == 'approved':
                share.status = 'approved'
                share.save()
                return redirect(reverse('share-detail', args=[uuid]))

        return render(request, self.template_name, context)