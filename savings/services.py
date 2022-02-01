from transactions.models import BankTransaction, Transaction
from authentication.models import User
from savings.models import Saving
import transactions.models as t_models
import shares.models as s_models

from django.core.exceptions import ObjectDoesNotExist

class SavingCrudService():

    def __init__(self, request):
        self.request = request
    
    
    def create_saving(self, data, created_by):
        #Retrieving data
        try:
            description = data['description']
            uuid = data['uuid']
            owner = data['owner']

            bank_transaction = BankTransaction.objects.get(id=uuid)

            if hasattr(bank_transaction, 'transaction'):
                print('ERROR, Bank transaction already assigned')
                return ('ERROR, Bank transaction already assigned', False, None)

            if not bank_transaction.type == 'credit':
                print('ERROR, Bank transaction reference type must be of type credit')
                return ('ERROR, Bank transaction reference type must be of type credit', False, None)

            transaction = Transaction.objects.create(
                    amount= bank_transaction.amount, 
                    description=bank_transaction.description,
                    reference=bank_transaction, 
                    type=bank_transaction.type,
                    status= t_models.TRANSACTION_STATUS[1][0],
                    created_by = created_by
            )

            owner = User.objects.get(email=owner)
            #Creating Share

            #Default Description
            if description == '':
                description = self._get_default_saving_description(owner, bank_transaction)

            saving = Saving.objects.create(
                description = description,
                status = s_models.SHARE_STATUS[1][0],
                owner = owner,
                transaction=transaction,
            )

            self._change_bank_transaction_status(bank_transaction, t_models.BANK_TRANSACTION_STATUS[1][0])

            return ('', True, saving)

        except KeyError as e:
            
            self._delete_transaction(transaction)
            print('ERROR, retrieving saving creation data: {}'.format(str(e)))
            return ('ERROR, retrieving saving creation data', False, None)

        except ObjectDoesNotExist as e:
            self._delete_transaction(transaction)
            print('ERROR, object does not exist: {}'.format(str(e)))
            return ('ERROR, object does not exist', False, None)

            
        except Exception as e:
            self._delete_transaction(transaction)
            print('ERROR, creating share: {}'.format(str(e)))
            return ('Error creating share', False, None)


    def delete_saving(self, saving):
        try:
            transaction = saving.transaction

            transaction.reference.status = t_models.BANK_TRANSACTION_STATUS[0][0]
            transaction.reference.save()

            transaction.delete()

            saving.delete()

            return ('', True, None)

        except Exception as e:
            return ('ERROR, deleting saving transaction: {}'.format(str(e)),False, transaction)


    def _delete_transaction(self, transaction):
        if transaction:
            return transaction.delete()
        return False

    def _change_bank_transaction_status(self, bank_transaction, status):

        if bank_transaction:
            bank_transaction.status = status
            bank_transaction.save()
            return True

        return False

    def _get_default_saving_description(self, owner, bank_transaction):
        return 'Saving: {}, {}'.format(owner.get_full_name(), bank_transaction.date_trans)
