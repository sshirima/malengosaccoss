

from django.urls.base import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django_tables2 import RequestConfig
from django.shortcuts import render
from django.contrib import messages
import shares.models as share_models
from shares.services import ShareCrudService

from transactions.models import BankTransaction, Transaction
from authentication.models import User
from django.db.models import Sum

from .forms import ShareCreateForm, ShareUpdateForm, ShareAuthorizationForm
from .models import Share
from .tables import ShareTable, ShareTableFilter
# Create your views here.


class ShareListView(LoginRequiredMixin, ListView):
    template_name ='shares/list.html'
    model = Share
    
    table_class = ShareTable
    table_data = Share.objects.all()
    paginate_by = 5
    filterset_class = ShareTableFilter
    context_filter_name = 'filter'

    def get_queryset(self, *args, **kwargs):
        qs = Share.objects.filter(transaction__created_by = self.request.user)
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self,*args, **kwargs):
        context = super(ShareListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = ShareTableFilter(self.request.GET, queryset=queryset)
        table = ShareTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 5}).configure(table)
        context['filter']=filter
        context['table']=table
        context['total_amount'] = queryset.aggregate(Sum('transaction__amount'))['transaction__amount__sum']

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

        service = ShareCrudService(self.request)
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
        context['owners'] = User.objects.all()
        context['bank_transaction'] = BankTransaction.objects.get(id=uuid)
        return context

class ShareDetailView(LoginRequiredMixin, DetailView):
    template_name = 'shares/detail.html'
    model = Share
    context_object_name = 'share'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):

        if self.request.user.is_admin:
            return Share.objects.filter(id=self.kwargs['id'])

        if self.request.user.is_authenticated:
            return Share.objects.filter( transaction__created_by=self.request.user)
        else:
            return Share.objects.none()


class ShareUpdateView(LoginRequiredMixin, UpdateView):
    template_name ='shares/update.html'
    model = Share
    context_object_name = 'share'
    form_class = ShareUpdateForm
    success_url = reverse_lazy('shares-list')
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def form_valid(self, form):
       
        #Create transaction first

        share = Share.objects.get(id=self.kwargs['id'])

        if share:
            share.description = form.cleaned_data['description']
            share.save()
            
            return HttpResponseRedirect(share.get_absolute_url())

        return super.form_invalid()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Share.objects.filter(transaction__created_by=self.request.user)
        else:
            return Share.objects.none()

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

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        service = ShareCrudService(self.request)
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