
from dataclasses import fields
import django_tables2 
from django_tables2.export import ExportMixin
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

class CommaSeparatedNumberColumn(django_tables2.Column):
    def render(self, value):
        return '{:0,.0f}'.format(value)


class BankTransactionTable(django_tables2.Table):
    selection = django_tables2.CheckBoxColumn(
        accessor="pk", 
        attrs = { "th__input": {"onclick": "toggle(this)"}},
        orderable=False,
    )
    amount = django_tables2.Column(accessor='amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = TypeColumn(accessor='type', verbose_name='Type')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    date_trans = django_tables2.Column(accessor='date_trans', verbose_name = "Tran Date")
    assign = django_tables2.TemplateColumn(template_name ='partials/_btn_assign.html', orderable=False)
    #date_updated = django_tables2.Column(accessor='date_updated', verbose_name = "Date Updated")
    #edit_delete = django_tables2.TemplateColumn(template_name ='partials/_update_delete.html')
    

    class Meta:
        model = BankTransaction
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('date_trans',)
        sequence = ('selection','amount','description','date_trans','status','type')
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("bank-transaction-detail", args=[record.id]), '{:0,.0f}'.format(record.amount)))
    
    def render_selection(self, record):
        if record.status == 'imported':
            return mark_safe('<input type="checkbox" name="selection" value="{}">'.format(record.id))
        return ''

class BankTransactionTableExport(django_tables2.Table):
    
    amount = CommaSeparatedNumberColumn(accessor='amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = django_tables2.Column(accessor='type', verbose_name='Type')
    status = django_tables2.Column(accessor='status', verbose_name = "Status")
    date_trans = django_tables2.Column(accessor='date_trans', verbose_name = "Trans Date")
    date_value = django_tables2.Column(accessor='date_value', verbose_name = "Value Date")
    balance = CommaSeparatedNumberColumn(accessor='balance', verbose_name = "Balance")
    created_by = django_tables2.Column(accessor='created_by', verbose_name = "Created By")
    
    class Meta:
        model = BankTransaction
        fields = ('amount','description','type','status','date_value','date_trans', 'balance', 'created_by')
        sequence = ('amount','description','type','status','date_value','date_trans', 'balance', 'created_by')

    def value_created_by(self,record):
        return record.created_by.email

class BankTransactionFlatTable(django_tables2.Table):
    
    amount = django_tables2.Column(accessor='amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = TypeColumn(accessor='type', verbose_name='Type')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    date_value = django_tables2.Column(accessor='date_value', verbose_name = "Value Date")
    
    class Meta:
        model = BankTransaction
        orderable = False
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('date_value',)
        sequence = ('amount','description','status','type','date_value')
    
    def render_amount(self,record):
        
        return mark_safe('<input type="hidden" onclick="toggle(this)" name="selection" value="{}"/>{}'.format(record.id, '{:0,.0f}'.format(record.amount)))#'{:0,.0f}'.format(record.amount)

class BankTransactionTableFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(label='Description', method='search_description')
    start_date = django_filters.CharFilter(label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(label='End Date', method='search_end_date')
    type = django_filters.CharFilter(label='Type', method='search_type')
    status = django_filters.CharFilter(label='Status', method='search_status')

    def search_description(self, qs, name, value):
        return qs.filter(Q(description__icontains=value)|Q(amount__icontains=value))

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

class TransactionTable(django_tables2.Table):
    amount = django_tables2.Column(accessor='reference__amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = StatusColumn(accessor='type', verbose_name='Type')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    date_trans = django_tables2.Column(accessor='reference__date_trans', verbose_name = "Tran Date")
    

    class Meta:
        model = Transaction
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('amount',)
        sequence = ('amount','description','date_trans','status','type')
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("transaction-detail", args=[record.id]), '{:0,.0f}'.format(record.amount)))

class TransactionTableExport(django_tables2.Table):
    amount = django_tables2.Column(accessor='reference.amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    type = django_tables2.Column(accessor='type', verbose_name='Type')
    status = django_tables2.Column(accessor='status', verbose_name = "Status")
    created_by = django_tables2.Column(accessor='created_by.email', verbose_name = "Created By")
    date_created = django_tables2.Column(accessor='date_created', verbose_name = "Date Created")
    

    class Meta:
        model = Transaction
        fields = ('amount','description','status','type','created_by','date_created')
        sequence = ('amount','description','status','type','created_by','date_created')

    def value_created_by(self,record):
        return record.created_by.email

    def value_date_created(self,record):
        return record.date_created.replace(tzinfo=None)

class TransactionTableFilter(django_filters.FilterSet):

    description = django_filters.CharFilter(label='Description', method='search_description')
    start_date = django_filters.CharFilter(label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(label='End Date', method='search_end_date')
    type = django_filters.CharFilter(label='Type', method='search_type')
    status = django_filters.CharFilter(label='Status', method='search_status')

    def search_description(self, qs, name, value):
        return qs.filter(Q(description__icontains=value)|Q(reference__amount__icontains=value))

    def search_start_date(self, qs, name, value):
        return qs.filter(Q(date_created__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(date_created__lte=value))

    def search_type(self, qs, name, value):
        return qs.filter(Q(type__iexact=value))

    def search_status(self, qs, name, value):
        return qs.filter(Q(status__iexact=value))
