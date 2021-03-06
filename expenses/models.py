from django.urls.base import reverse
from django.db import models
from members.models import Member
import uuid


from transactions.models import Transaction
# Create your models here.
EXPENSE_STATUS = (
    ('pending', 'PENDING' ),
    ('approved', 'APPROVED' ),
    ('cancelled', 'CANCELLED'),
)

class Expense(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=EXPENSE_STATUS, default='pending')
    owner = models.ForeignKey(Member,blank=True, null=True, on_delete=models.DO_NOTHING)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.transaction.amount)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ['-transaction__reference__date_trans']

    def get_absolute_url(self):
        return reverse('expense-detail', args=[self.id])

