from pyexpat import model
from django.contrib import admin

from authentication.models import User
from members.models import Member

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active','is_staff','is_admin','password_change', )
    search_fields = ['email']
    ordering = ['email']
    exclude = ('first_name','last_name','username')
    readonly_fields = ('email','date_joined','last_login','password')


admin.site.register(Member)