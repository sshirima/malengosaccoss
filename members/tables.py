
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
    mobile_number = django_tables2.Column( accessor='mobile_number', verbose_name='Phone')
    is_active = BooleanColumn( accessor='user__is_active', verbose_name='Is active', )
    is_staff = BooleanColumn( accessor='user__is_staff', verbose_name='Is staff')
    password_change = BooleanColumn( accessor='user__password_change', verbose_name='Change password')
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
        sequence = ('fullname','email', 'gender','mobile_number','is_active','is_staff','password_change')
    
    def render_fullname(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("member-detail", args=[record.id]), record.get_full_name()))

class MemberTableExport(django_tables2.Table):
    first_name = django_tables2.Column(accessor='first_name', verbose_name='First Name')
    middle_name = django_tables2.Column(accessor='middle_name', verbose_name='Middle Name')
    last_name = django_tables2.Column(accessor='last_name', verbose_name='Last Name')
    gender = django_tables2.Column(accessor='gender', verbose_name='Gender')
    mobile_number = django_tables2.Column( accessor='mobile_number', verbose_name='Mobile Number')
    is_active = django_tables2.Column( accessor='is_active', verbose_name='Is Active', )
    is_staff = django_tables2.Column( accessor='user__is_staff', verbose_name='Is Staff')
    email = django_tables2.Column(accessor='user__email', verbose_name = "Email")
    

    class Meta:
        model = Member
        fields = ('first_name', 'middle_name','last_name','gender','mobile_number','is_active','is_staff','email')
        sequence = ('first_name', 'middle_name','last_name','gender','mobile_number','is_active','is_staff','email')


class MemberTableFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label='Name', method='search_names')
    gender = django_filters.CharFilter(label='Gender', method='search_gender')
    status = django_filters.CharFilter(label='Status', method='search_status')


    def search_names(self, qs, name, value):
        return qs.filter(
            Q(first_name__icontains=value)|
            Q(middle_name__icontains=value)|
            Q(last_name__icontains=value)|
            Q(user__email__icontains=value)|
            Q(mobile_number__icontains=value)
            )

    def search_gender(self, qs, name, value):
        return qs.filter(Q(gender__exact=value))

    def search_status(self, qs, name, value):
        isActive = True if value == 'active' else False
        return qs.filter(Q(is_active__exact=isActive))

    class Meta:
        model = Member
        fields = ['name','gender','status']