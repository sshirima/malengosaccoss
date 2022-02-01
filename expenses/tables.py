
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
    reference = django_tables2.Column(accessor='transaction.description', verbose_name='Reference Transaction')
    status = StatusColumn(accessor='status', verbose_name = "Status")
    owner = django_tables2.Column(accessor='owner.email', verbose_name='Owned By')
    date_created = django_tables2.Column(accessor='date_created', verbose_name = "Date Created")
    edit_delete = django_tables2.TemplateColumn(template_name ='partials/_btn_update_delete_expense.html')
    

    class Meta:
        model = Expense
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('date_created',)
        sequence = ('amount', 'description','reference','status','owner','date_created','edit_delete')
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("saving-detail", args=[record.id]), record.transaction.amount))

    def render_reference(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("transaction-detail", args=[record.transaction.id]), record.transaction.description))


class ExpenseTableFilter(django_filters.FilterSet):
    description = django_filters.CharFilter(label='Description', method='search_description')

    def search_description(self, qs, name, value):
        return qs.filter(Q(description__icontains=value))

    class Meta:
        model = Expense
        fields = ['description']