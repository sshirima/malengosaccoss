from django.urls.base import reverse
from django.db import models
from authentication.models import User
import uuid
# Create your models here.
TRANSACTION_STATUS = (
    ('pending', 'Pending' ),
    ('approved', 'Approved' ),
    ('cancelled', 'Canceled'),
)

TRANSACTION_TYPE = (
    ('debit', 'Debit' ),
    ('credit', 'Credit' ),
)

BANK_TRANSACTION_STATUS = (
    ('imported', 'Imported' ),
    ('assigned', 'Assigned' ),
    ('cancelled', 'Canceled'),
)

class BankTransaction(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    amount = models.FloatField()
    description = models.CharField(max_length=255, null=True)
    instrument_id = models.CharField(max_length=30, blank=True, null=True)
    balance = models.FloatField()
    type = models.CharField(max_length=20,choices=TRANSACTION_TYPE)
    status = models.CharField(max_length=20, choices=BANK_TRANSACTION_STATUS)
    created_by = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)

    date_trans = models.DateField()
    date_value = models.DateField()
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}:{}".format(str(self.type), str(self.amount))

    class Meta:
        ordering = ['-date_created']

    def get_absolute_url(self):
        return reverse('banktransaction-detail', args=[self.id])


class Transaction(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    amount = models.FloatField()
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20,choices=TRANSACTION_TYPE,  blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    reference = models.OneToOneField(BankTransaction, on_delete=models.CASCADE)
    created_by = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)

    class Meta:
        ordering = ['-date_created']

    def get_absolute_url(self):
        return reverse('transaction-detail', args=[self.id])


