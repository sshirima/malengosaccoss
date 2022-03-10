from django.contrib import admin
from .models import (
    Loan, 
    LoanFormFee, 
    LoanInterest, 
    LoanProcessingFee, 
    LoanRepayment, 
    LoanInsuranceFee,
    LoanLimits
)

# Register your models here.
@admin.register(LoanFormFee)
class LoanFormFeeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'status', 'created_by')
    search_fields = ('amount', )
    

@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'created_by')
    search_fields = ('loan', )

@admin.register(LoanInterest)
class LoanInterestAdmin(admin.ModelAdmin):
    list_display = ('percentage', 'status')
    search_fields = ('percentage', )

@admin.register(LoanProcessingFee)
class LoanProcessingFeeAdmin(admin.ModelAdmin):
    list_display = ('percentage', 'status')
    search_fields = ('percentage', )

@admin.register(LoanInsuranceFee)
class LoanInsuranceFeeAdmin(admin.ModelAdmin):
    list_display = ('percentage', 'status')
    search_fields = ('percentage', )

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('principle', 'interest_rate')
    search_fields = ('principle',)

@admin.register(LoanLimits)
class LoanLimitsAdmin(admin.ModelAdmin):
    list_display = ('max_principle', 'max_duration','type', 'status')
    search_fields = ('principle',)