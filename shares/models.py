from django.urls.base import reverse
from django.db import models
from authentication.models import User
import uuid


from transactions.models import Transaction
# Create your models here.
SHARE_STATUS = (
    ('pending', 'PENDING' ),
    ('approved', 'APPROVED' ),
    ('cancelled', 'CANCELLED'),
)

class Share(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=SHARE_STATUS, default='pending')
    owner = models.ForeignKey(User,blank=True, null=True, on_delete=models.DO_NOTHING)
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.transaction.amount)

    class Meta:
        ordering = ['-date_created']

    def get_absolute_url(self):
        return reverse('share-detail', args=[self.id])

