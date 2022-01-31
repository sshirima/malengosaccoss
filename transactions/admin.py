import imp
from django.contrib import admin

from .models import Transaction, BankTransaction

# Register your models here.
admin.site.register(Transaction)
admin.site.register(BankTransaction)