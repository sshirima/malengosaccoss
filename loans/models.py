from tabnanny import verbose
from django.db import models
from django.urls.base import reverse
import uuid
from authentication.models import User
from members.models import Member
from transactions.models import Transaction

# Create your models here.
INTEREST_STATUS = (
    ('active', 'Active' ),
    ('inactive', 'Inactive' ),
)

LOAN_STATUS = (
    ('pending', 'Pending' ),
    ('issued', 'Issued' ),
)

LOAN_TYPE = (
    ('normal', 'Normal' ),
    ('emergence', 'Emergence' ),
)

LOAN_REPAYMENT_STATUS = (
    ('issued', 'Normal' ),
    ('repayment', 'Repayment' ),
    ('completed', 'Completed' ),
    ('default', 'Default' ),
)

class LoanBaseModel(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    created_by = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        abstract = True


class LoanInterest(LoanBaseModel):
    percentage = models.FloatField()
    status = models.CharField(max_length=20, choices=INTEREST_STATUS, default='inactive')
    type = models.CharField(max_length=20, choices=LOAN_TYPE, default='normal')
    
    def __str__(self):
        return str(self.percentage)

    class Meta:
        ordering = ['-date_created']

class LoanProcessingFee(LoanBaseModel):
    percentage = models.FloatField()
    status = models.CharField(max_length=20, choices=INTEREST_STATUS, default='inactive')
    
    def __str__(self):
        return str(self.percentage)

    class Meta:
        ordering = ['-date_created']


class LoanInsuranceFee(LoanBaseModel):
    percentage = models.FloatField()
    status = models.CharField(max_length=20, choices=INTEREST_STATUS, default='inactive')
    
    def __str__(self):
        return str(self.percentage)

    class Meta:
        ordering = ['-date_created']

class LoanFormFee(LoanBaseModel):
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=INTEREST_STATUS, default='inactive')
    type = models.CharField(max_length=20, choices=LOAN_TYPE, default='normal')

    def __str__(self):
        return str(self.amount)

    class Meta:
        ordering = ['-date_created']


class LoanLimits(LoanBaseModel):
    type = models.CharField(max_length=20, choices=LOAN_TYPE, default='normal')
    max_principle = models.FloatField()
    max_duration = models.FloatField()
    status = models.CharField(max_length=20, choices=INTEREST_STATUS, default='inactive')

    def __str__(self):
        return 'Max Principle: {},Max Duration: {}'.format(str(self.max_principle),str(self.max_duration))

    class Meta:
        verbose_name = "LoanLimits"
        verbose_name_plural = "Loan Limits"

class Loan(LoanBaseModel):
    principle = models.FloatField(editable = False)
    duration = models.FloatField(editable = False)
    interest_rate = models.FloatField(editable = False)
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='pending')
    type = models.CharField(max_length=20, choices=LOAN_TYPE, default='normal')
    member = models.ForeignKey(to=Member, on_delete=models.DO_NOTHING, editable = False)
    amount_issued = models.FloatField(editable = False)
    loan_fee = models.FloatField(editable = False)
    insurance_fee = models.FloatField(editable = False)
    form_fee = models.FloatField(editable = False)
    interest_amount = models.FloatField(editable = False)
    installment_amount = models.FloatField(editable = False)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    repayment_status = models.CharField(max_length=20, choices=LOAN_REPAYMENT_STATUS, default='issued')

    def __str__(self):
        return str(self.principle)

    class Meta:
        verbose_name = "Loan"

    def get_absolute_url(self):
        return reverse('loan-detail', args=[self.id])


    def get_total_loan_amount(self):
        return self.principle + self.interest_amount

class LoanRepayment(LoanBaseModel):
    loan = models.ForeignKey(to=Loan, on_delete=models.CASCADE, default=None)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('loanrepayment-detail', args=[self.id])