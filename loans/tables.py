
import django_tables2 
import django_filters
from django.utils.safestring import mark_safe
from django.db.models import Q
from django_tables2.utils import A  # alias for Accessor
from django.urls.base import reverse

from .models import Loan, LoanRepayment

class StatusColumn(django_tables2.Column):
    def render(self, value):
        if value.lower() == 'issued':
            return mark_safe('<span class="badge badge-success">{}</span>'.format(value))

        else :
            return mark_safe('<span class="badge badge-warning">{}</span>'.format(value))

class LoanTable(django_tables2.Table):
    
    principle = django_tables2.Column(accessor='principle', verbose_name='Principle')
    duration = django_tables2.Column(accessor='duration', verbose_name='Duration')
    date_trans = django_tables2.Column(accessor='transaction.reference.date_trans', verbose_name = "Date Trans")
    member = django_tables2.Column(accessor='status', verbose_name = "Belongs To")
    installment_amount = django_tables2.Column(accessor='installment_amount', verbose_name = "Installment Amount")
    status = StatusColumn(accessor='status', verbose_name = "Status")
    type = django_tables2.Column(accessor='type', verbose_name = "Type")
    

    class Meta:
        model = Loan
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('principle','installment_amount','duration','member','date_trans','status','type')
        sequence = ('principle','installment_amount','member','date_trans','duration','status','type')
    
    def render_principle(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("loan-detail", args=[record.id]), '{:0,.0f}'.format(record.principle)))

    def render_member(self,record):
        return record.member.get_full_name()

    def render_amount_issued(self, record):
        return '{:0,.0f}'.format(record.amount_issued)

    def render_interest(self, record):
        return '{:0,.0f}'.format(record.interest_amount)

    def render_installment_amount(self, record):
        return '{:0,.0f}'.format(record.installment_amount)

    def render_duration(self, record):
        return '{:0,.0f}'.format(record.duration)

class LoanTableExport(django_tables2.Table):
    
    principle = django_tables2.Column(accessor='principle', verbose_name='Principle')
    duration = django_tables2.Column(accessor='duration', verbose_name='Duration(m)')
    interest = django_tables2.Column(accessor='interest_amount', verbose_name='Interest')
    member = django_tables2.Column(accessor='status', verbose_name = "Member")
    amount_issued = django_tables2.Column(accessor='amount_issued', verbose_name = "Issued Amount")
    installment_amount = django_tables2.Column(accessor='installment_amount', verbose_name = "Installment Amount")
    status = django_tables2.Column(accessor='status', verbose_name = "Status")
    type = django_tables2.Column(accessor='type', verbose_name = "Type")
    date_issued = django_tables2.Column(accessor='date_created', verbose_name = "Date Issued")
    date_created = django_tables2.Column(accessor='date_created', verbose_name = "Date Created")

    class Meta:
        model = Loan
        fields = ('principle','duration','interest','amount_issued','member','installment_amount','status','type','date_created','date_issued')
        sequence = ('principle','duration','interest','amount_issued','installment_amount','member','status','type','date_created','date_issued')

    def value_member(self,record):
        return record.member.get_full_name()

    def value_date_issued(self,record):
        return record.transaction.reference.date_trans

    def value_date_created(self,record):
        return record.date_created.replace(tzinfo=None)

class LoanTableFilter(django_filters.FilterSet):
    member = django_filters.CharFilter(label='Member', method='search_member')
    start_date = django_filters.CharFilter(label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(label='End Date', method='search_end_date')
    type = django_filters.CharFilter(label='Type', method='search_type')
    status = django_filters.CharFilter(label='Status', method='search_status')

    def search_member(self, qs, name, value):
        return qs.filter(
            Q(member__first_name__icontains=value)|
            Q(member__middle_name__icontains=value)|
            Q(member__last_name__icontains=value)
            )

    def search_start_date(self, qs, name, value):
        return qs.filter(Q(date_created__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(date_created__lte=value))

    def search_type(self, qs, name, value):
        return qs.filter(Q(type__iexact=value))

    def search_status(self, qs, name, value):
        return qs.filter(Q(status__iexact=value))

    

    class Meta:
        model = Loan
        fields = ['member']

class LoanRepaymentTable(django_tables2.Table):
    
    amount = django_tables2.Column(accessor='transaction__amount', verbose_name='Paid Amount')
    loan = django_tables2.Column(accessor='loan', verbose_name='Reference Loan')
    member = django_tables2.Column(accessor='loan__member', verbose_name = "Owner")
    date_paid = django_tables2.Column(accessor='loan__transaction__reference__date_trans', verbose_name = "Date Paid")

    class Meta:
        model = LoanRepayment
        attrs = {'class': 'table'}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('amount','member','date_paid')
        sequence = ('amount','loan','member','date_paid')
    
    def render_amount(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("loanrepayment-detail", args=[record.id]), '{:0,.0f}'.format(record.transaction.amount)))

    def render_member(self,record):
        return record.loan.member.get_full_name()

    def render_loan(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("loan-detail", args=[record.id]), '{:0,.0f}'.format(record.loan.principle)))

class LoanRepaymentTableExport(django_tables2.Table):
    
    amount = django_tables2.Column(accessor='transaction__amount', verbose_name='Paid Amount')
    member = django_tables2.Column(accessor='loan__member', verbose_name = "Owner")
    date_paid = django_tables2.Column(accessor='loan__transaction__reference__date_trans', verbose_name = "Date Paid")

    class Meta:
        model = LoanRepayment
        fields = ('amount','member','date_paid')
        sequence = ('amount','member','date_paid')
    
    def value_member(self,record):
        return record.loan.member.get_full_name()

class LoanRepaymentTableFilter(django_filters.FilterSet):
    member = django_filters.CharFilter(label='Member', method='search_member')
    start_date = django_filters.CharFilter(label='Start Date', method='search_start_date')
    end_date = django_filters.CharFilter(label='End Date', method='search_end_date')

    def search_member(self, qs, name, value):
        return qs.filter(
            Q(loan__member__first_name__icontains=value)|
            Q(loan__member__middle_name__icontains=value)|
            Q(loan__member__last_name__icontains=value)
            
            )

    def search_start_date(self, qs, name, value):
        return qs.filter(Q(loan__transaction__reference__date_trans__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(loan__transaction__reference__date_trans__lte=value))


