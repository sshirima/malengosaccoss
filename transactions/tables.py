
import django_tables2 
import django_filters
from django.utils.safestring import mark_safe
from django.db.models import Q
from django_tables2.utils import A  # alias for Accessor
from django.urls.base import reverse

from .models import BankTransaction, Transaction

class StatusColumn(django_tables2.Column):
    def render(self, value):
        if value.lower() == 'pending':
            return mark_safe('<span class="badge badge-warning">{}</span>'.format(value))

        elif value.lower() == 'cancelled':
            return mark_safe('<span class="badge badge-danger">{}</span>'.format(value))

        elif value.lower() == 'imported':
            return mark_safe('<span class="badge badge-warning">{}</span>'.format(value))

        elif value.lower() == 'debit':
            return mark_safe('<span class="badge badge-danger">{}</span>'.format(value))

        else :
            return mark_safe('<span class="badge badge-success">{}</span>'.format(value))

class TypeColumn(django_tables2.Column):
    def render(self, value):
        if value.lower() == 'credit':
            return mark_safe('<small class="text-success mr-1"><i class="fas fa-arrow-down"></i>{}</small>'.format(value))

        elif value.lower() == 'debit':
            return mark_safe('<small class="text-danger mr-1"><i class="fas fa-arrow-up"></i>{}</small>'.format(value))

        else :
            return mark_safe('<small class="text-info mr-1"><i class="fas fa-exclamation"></i>{}</small>">{}</span>'.format(value))


class BankTransactionTable(django_tables2.Table):
    amount = django_tables2.Column(accessor='amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = TypeColumn(accessor='type', verbose_name='Type')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    date_value = django_tables2.Column(accessor='date_value', verbose_name = "Value Date")
    assign = django_tables2.TemplateColumn(template_name ='partials/_btn_assign.html')
    #date_updated = django_tables2.Column(accessor='date_updated', verbose_name = "Date Updated")
    #edit_delete = django_tables2.TemplateColumn(template_name ='partials/_update_delete.html')
    

    class Meta:
        model = BankTransaction
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('date_value',)
        sequence = ('amount','description','status','type','date_value')
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("bank-transaction-detail", args=[record.id]), '{:0,.0f}'.format(record.amount)))


class TransactionTable(django_tables2.Table):
    amount = django_tables2.Column(accessor='reference.amount', verbose_name='Amount(Tsh)')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = StatusColumn(accessor='type', verbose_name='Type')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    created_by = django_tables2.Column(accessor='created_by.email', verbose_name = "Created By")
    date_created = django_tables2.Column(accessor='date_updated', verbose_name = "Date Updated")
    #edit_delete = django_tables2.TemplateColumn(template_name ='partials/_update_delete.html')
    

    class Meta:
        model = Transaction
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('amount',)
        sequence = ('amount','description','status','type','created_by','date_created')
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("transaction-detail", args=[record.id]), '{:0,.0f}'.format(record.amount)))

class BankTransactionTableFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(label='Description', method='search_description')
    start_date = django_filters.CharFilter(label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(label='End Date', method='search_end_date')
    type = django_filters.CharFilter(label='Type', method='search_type')
    status = django_filters.CharFilter(label='Status', method='search_status')

    def search_description(self, qs, name, value):
        return qs.filter(Q(description__icontains=value))

    def search_start_date(self, qs, name, value):
        return qs.filter(Q(date_trans__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(date_trans__lte=value))

    def search_type(self, qs, name, value):
        return qs.filter(Q(type__iexact=value))

    def search_status(self, qs, name, value):
        return qs.filter(Q(status__iexact=value))

    class Meta:
        model = BankTransaction
        fields = ['description', 'start_date', 'end_date', 'type','status']


class TransactionTableFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(label='Description', method='search_description')

    def search_description(self, qs, name, value):
        return qs.filter(Q(description__icontains=value))

    class Meta:
        model = Transaction
        fields = ['description']
