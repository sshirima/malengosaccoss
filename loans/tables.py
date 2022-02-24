
import django_tables2 
import django_filters
from django.utils.safestring import mark_safe
from django.db.models import Q
from django_tables2.utils import A  # alias for Accessor
from django.urls.base import reverse

from .models import Loan

class StatusColumn(django_tables2.Column):
    def render(self, value):
        if value.lower() == 'issued':
            return mark_safe('<span class="badge badge-success">{}</span>'.format(value))

        else :
            return mark_safe('<span class="badge badge-warning">{}</span>'.format(value))

class LoanTable(django_tables2.Table):
    
    principle = django_tables2.Column(accessor='principle', verbose_name='Principle')
    interest = django_tables2.Column(accessor='interest_rate', verbose_name='Interest')
    duration = django_tables2.Column(accessor='duration', verbose_name='Duration(m)')
    member = django_tables2.Column(accessor='status', verbose_name = "Member")
    amount_issued = django_tables2.Column(accessor='amount_issued', verbose_name = "Issued Amount")
    status = StatusColumn(accessor='status', verbose_name = "Status")
    type = django_tables2.Column(accessor='type', verbose_name = "Type")
    

    class Meta:
        model = Loan
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('principle',)
        sequence = ('principle','amount_issued','interest','duration','member','status','type')
    
    def render_principle(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("loan-detail", args=[record.id]), '{:0,.0f}'.format(record.principle)))

    def render_member(self,record):
        return record.member.get_full_name()

    def render_amount_issued(self, record):
        return '{:0,.0f}'.format(record.amount_issued)

    def render_duration(self, record):
        return '{:0,.0f}'.format(record.duration)


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
        return qs.filter(Q(transaction__reference__date_trans__gte=value))

    def search_end_date(self, qs, name, value):
        return qs.filter(Q(transaction__reference__date_trans__lte=value))

    def search_type(self, qs, name, value):
        return qs.filter(Q(type__iexact=value))

    def search_status(self, qs, name, value):
        return qs.filter(Q(status__iexact=value))

    

    class Meta:
        model = Loan
        fields = ['member']
