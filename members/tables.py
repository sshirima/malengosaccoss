
import django_tables2 
import django_filters
from django.utils.safestring import mark_safe
from django.db.models import Q
from django_tables2.utils import A  # alias for Accessor
from django.urls.base import reverse

from .models import Member

class BooleanColumn(django_tables2.Column):
    def render(self, value):
        if value:
            return mark_safe('<small class="text-success mr-1"><i class="fas fa-check-circle"></i></i></small>')
        else:
            return mark_safe('<small class="text-danger mr-1"><i class="fas fa-times-circle"></i></i></small>')

class MemberTable(django_tables2.Table):
    fullname = django_tables2.Column(accessor='first_name', verbose_name='Full name')
    gender = django_tables2.Column(accessor='gender', verbose_name='Gender')
    mobile_number = django_tables2.Column( accessor='mobile_number', verbose_name='Mobile Number')
    is_active = BooleanColumn( accessor='is_active', verbose_name='Is Active', )
    is_staff = BooleanColumn( accessor='user__is_staff', verbose_name='Is Staff')
    email = django_tables2.Column(accessor='user__email', verbose_name = "Email")
    
    # assign = django_tables2.TemplateColumn(template_name ='partials/_btn_assign.html')
    #date_updated = django_tables2.Column(accessor='date_updated', verbose_name = "Date Updated")
    #edit_delete = django_tables2.TemplateColumn(template_name ='partials/_update_delete.html')
    #attrs={"th": {"class": "d-none d-sm-block"}, "td": {"class": "d-none d-sm-block"}},
    

    class Meta:
        model = Member
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('gender',)
        sequence = ('fullname', 'gender','mobile_number','email','is_active','is_staff')
    
    def render_fullname(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("member-detail", args=[record.id]), record.get_full_name()))


class MemberTableFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(label='Email', method='search_email')

    def search_email(self, qs, name, value):
        return qs.filter(Q(user__email__icontains=value))

    class Meta:
        model = Member
        fields = ['email']