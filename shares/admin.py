from django.contrib import admin
from .models import Share
# Register your models here.
@admin.register(Share)
class ShareormFeeAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'status', 'date_created')
    search_fields = ('description', )