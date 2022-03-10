import imp
from django.contrib import admin
from .models import Saving

# Register your models here.
@admin.register(Saving)
class SavingFormFeeAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'status', 'date_created')
    search_fields = ('description', )
