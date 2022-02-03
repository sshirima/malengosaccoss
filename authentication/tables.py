
import django_tables2 
import django_filters
from django.utils.safestring import mark_safe
from django.db.models import Q
from django_tables2.utils import A  # alias for Accessor
from django.urls.base import reverse

from .models import User

class BooleanColumn(django_tables2.Column):
    def render(self, value):
        if value:
            return mark_safe('<small class="text-success mr-1"><i class="fas fa-check-circle"></i></i></small>')
        else:
            return mark_safe('<small class="text-danger mr-1"><i class="fas fa-times-circle"></i></i></small>')

class MemberTable(django_tables2.Table):
    first_name = django_tables2.Column(accessor='first_name', verbose_name='First Name')
    last_name = django_tables2.Column(accessor='last_name', verbose_name='Last Name')
    mobile_number = django_tables2.Column(accessor='mobile_number', verbose_name='Mobile Number')
    is_active = BooleanColumn(accessor='is_active', verbose_name='Is Active')
    is_staff = BooleanColumn(accessor='is_staff', verbose_name='Is Staff')
    is_admin = BooleanColumn(accessor='is_admin', verbose_name='Is Admin')
    
    email = django_tables2.Column(accessor='email', verbose_name = "Email")
    # assign = django_tables2.TemplateColumn(template_name ='partials/_btn_assign.html')
    #date_updated = django_tables2.Column(accessor='date_updated', verbose_name = "Date Updated")
    #edit_delete = django_tables2.TemplateColumn(template_name ='partials/_update_delete.html')
    

    class Meta:
        model = User
        attrs = {'class': 'table '}
        template_name = 'django_tables2/bootstrap.html'
        fields = ('first_name',)
        sequence = ('email', 'first_name','last_name',)
    
    def render_email(self,record):
        return mark_safe('<a href="{}">{}</a>'.format(reverse("member-detail", args=[record.id]), record.email))


class MemberTableFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(label='Email', method='search_email')

    def search_email(self, qs, name, value):
        return qs.filter(Q(email__icontains=value))

    class Meta:
        model = User
        fields = ['email']
