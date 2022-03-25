
import django_tables2 
import django_filters
from django.utils.safestring import mark_safe
from django.db.models import Q
from django_tables2.utils import A  # alias for Accessor
from django.urls.base import reverse

from .models import Expense

class StatusColumn(django_tables2.Column):
    def render(self, value):
        if value.lower() == 'pending':
            return mark_safe('<span class="badge badge-warning">{}</span>'.format(value))

        elif value.lower() == 'cancelled':
            return mark_safe('<span class="badge badge-danger">{}</span>'.format(value))
        else :
            return mark_safe('<span class="badge badge-success">{}</span>'.format(value))


class ExpenseTable(django_tables2.Table):
    amount = django_tables2.Column(accessor='transaction.amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    date_trans = django_tables2.Column(accessor='transaction.reference.date_trans', verbose_name = "Date Trans")
    

    class Meta:
        model = Expense
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('amount', 'description','date_trans','status',)
        sequence = ('amount', 'description','date_trans','status',)
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("expense-detail", args=[record.id]), '{:0,.0f}'.format(record.transaction.amount)))

class ExpenseTableExport(django_tables2.Table):
    amount = django_tables2.Column(accessor='transaction.amount', verbose_name='Amount')
    description = django_tables2.Column(accessor='description', verbose_name='Description')
    status = django_tables2.Column(accessor='status', verbose_name = "Status")
    date_trans = django_tables2.Column(accessor='transaction.reference.date_trans', verbose_name = "Date Trans")
    date_created = django_tables2.Column(accessor='date_created', verbose_name = "Date Created")

    class Meta:
        model = Expense
        fields = ('amount', 'description','date_trans','status',)
        sequence = ('amount', 'description','date_trans','status',)

    def value_date_created(self,record):
        return record.date_created.replace(tzinfo=None)

class ExpenseTableFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(label='Description', method='search_description')
    start_date = django_filters.CharFilter(label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(label='End Date', method='search_end_date')

    def search_description(self, qs, name, value):
        return qs.filter(
            Q(description__icontains=value)
            )

    def search_start_date(self, qs, name, value):
        return qs.filter(Q(date_created__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(date_created__lte=value))