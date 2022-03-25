from django.urls.base import reverse
from django.db import models
import traceback

from authentication.models import User
import uuid

from members.models import Member
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

TRANSACTION_TYPE_ACTIONS = {
    'debit':{
        'actions':{
            'assign_to_loans':'Assign to Loans',
            'assign_to_expenses':'Assign to Expenses'
        }
    },
    'credit':{
        'actions':{
            'assign_to_shares':'Assign to Shares',
            'assign_to_savings':'Assign to Savings',
            'assign_to_loanrepayments':'Assign to Loan Repayments'
        }
    },

}

def get_transaction_assignment_action_by_type(type, as_items=False):
    try:
        if as_items:
            return TRANSACTION_TYPE_ACTIONS[type]['actions'].items()
        return TRANSACTION_TYPE_ACTIONS[type]['actions']
    except KeyError as e:
        print('ERROR, get transaction assignment action by type: {}'.format(str(e)))
        return {}

def get_transaction_assignment_action_all(as_items=False):
    actions = {}
    try:
        for key, value in TRANSACTION_TYPE_ACTIONS.items():
            actions.update(TRANSACTION_TYPE_ACTIONS[key]['actions'])
        
        if as_items:
            return actions.items()
        return actions
        
    except KeyError as e:
        print('ERROR, get transaction assignment action all: {}'.format(str(e)))
        return {}

def get_transaction_assignment_action_by_key(key):
    all_assignment = get_transaction_assignment_action_all()
    return (key, all_assignment[key])
    

class BaseTransaction(models.Model):
    id = models.UUIDField(primary_key = True,default = uuid.uuid4, editable = False)
    type = models.CharField(max_length=20,choices=TRANSACTION_TYPE)
    created_by = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    

    class Meta:
        abstract = True

class BankTransaction(BaseTransaction):
    
    amount = models.FloatField()
    description = models.CharField(max_length=255, null=True)
    instrument_id = models.CharField(max_length=30, blank=True, null=True)
    balance = models.FloatField()
    status = models.CharField(max_length=20, choices=BANK_TRANSACTION_STATUS)
    date_trans = models.DateField()
    date_value = models.DateField()
    

    def __str__(self):
        return "{}:{}".format(str(self.type), str(self.amount))

    class Meta:
        ordering = ['-date_trans']

    def get_absolute_url(self):
        return reverse('banktransaction-detail', args=[self.id])


class Transaction(BaseTransaction):
    amount = models.FloatField()
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    reference = models.OneToOneField(BankTransaction, on_delete=models.CASCADE)
    

    def __str__(self):
        return str(self.amount)

    class Meta:
        ordering = ['-reference__date_trans']

    def get_absolute_url(self):
        return reverse('transaction-detail', args=[self.id])

    def get_ralated_list(self):
        related_list = []
        # get all the related object
        for rel in self._meta.get_fields():
            try:
                # check if there is a relationship with at least one related object
                related = rel.related_model.objects.filter(**{rel.field.name: self})
                if related.exists():
                    related_list.append(related)
                    # if there is return a Tuple of flag = False the related_model object
            except AttributeError as e:  # an attribute error for field occurs when checking for AutoField
                #traceback.print_exc()
                pass # just pass as we dont need to check for AutoField
        return related_list