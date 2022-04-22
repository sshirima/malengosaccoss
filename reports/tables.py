from pyexpat import model
import django_tables2
import django_filters
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.urls.base import reverse

from transactions.models import BankTransaction


class ReportTransactionsTable(django_tables2.Table):
    month = django_tables2.Column(
        accessor='month', verbose_name='Month')
    total_credit = django_tables2.Column(
        accessor='total_credit', verbose_name='Total Credit')
    total_debit = django_tables2.Column(
        accessor='total_debit', verbose_name='Total Debit')
    balance = django_tables2.Column(
        accessor='total_debit', verbose_name='Balance')

    class Meta:
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('month',)
        sequence = ('month', 'total_credit','total_debit','balance')

    def render_total_credit(self,record):
        return '{:0,.0f}'.format(record['total_credit'])

    def render_total_debit(self,record):
        return '{:0,.0f}'.format(record['total_debit'])
        
    def render_balance(self,record):
        balance = record['total_credit'] - record['total_debit']
        if balance > 0:
            return mark_safe('<span class="badge badge-success">{}</span>'.format('{:0,.0f}'.format(balance)))
        return mark_safe('<span class="badge badge-danger">{}</span>'.format('{:0,.0f}'.format(balance)))


class ReportMembersTable(django_tables2.Table):
    name = django_tables2.Column(accessor='email', verbose_name='Member Name')
    share_total = django_tables2.Column(accessor='share_total', verbose_name='Total Share')
    saving_total = django_tables2.Column(accessor='saving_total', verbose_name='Total Saving')
    loan_total = django_tables2.Column(accessor='loan_total', verbose_name='Total Loan')

    class Meta:
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('name', 'share_total','saving_total','loan_total')
        sequence = ('name', 'share_total','saving_total','loan_total')

    def render_name(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("member-detail", args=[record['id']]), '{} {} {}'.format(record['first_name'], record['middle_name'], record['last_name'])))

    # def render_name(self,record):
    #     return '{} {} {}'.format(record['first_name'], record['middle_name'], record['last_name'])

    def render_share_total(self,record):
        return '{:0,.0f}'.format(record['share_total'])

    def render_saving_total(self,record):
        return '{:0,.0f}'.format(record['saving_total'])
        
    def render_loan_total(self,record):
        return '{:0,.0f}'.format(record['loan_total'])



class ReportTransactionTableFilter(django_filters.FilterSet):
    start_date = django_filters.CharFilter(
        label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(
        label='End Date', method='search_end_date')

    def search_start_date(self, qs, name, value):
        return qs.filter(Q(date_created__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(date_created__lte=value))
