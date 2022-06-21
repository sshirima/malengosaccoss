import imp
from django.contrib import admin

from .models import BankStatement, Transaction, BankTransaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(BankTransaction)

@admin.register(BankStatement)
class UserAdmin(admin.ModelAdmin):
    list_display = ('filename', 'date_created','created_by', )
    search_fields = ['filename']
    ordering = ['filename']
    readonly_fields = ('date_created','created_by','filename')