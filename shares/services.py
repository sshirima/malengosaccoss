from members.models import Member
from transactions.models import BankTransaction, Transaction
from authentication.models import User
from shares.models import Share
import transactions.models as t_models
import shares.models as s_models

from django.core.exceptions import ObjectDoesNotExist

class ShareCrudService():
    
    def create_share(self, data, created_by):
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

            owner = Member.objects.get(id=owner)
            #Creating Share
            #Default Description
            if description == '':
                description = self._get_default_share_description(owner, bank_transaction)
                
            share = Share.objects.create(
                description = description,
                status = s_models.SHARE_STATUS[1][0],
                owner = owner,
                transaction=transaction,
            )

            self._change_bank_transaction_status(bank_transaction, t_models.BANK_TRANSACTION_STATUS[1][0])

            return ('', True, share)

        except KeyError as e:
            
            self._delete_transaction(transaction)
            print('ERROR, retrieving share creation data: {}'.format(str(e)))
            return ('ERROR, retrieving share creation data', False, None)

        except ObjectDoesNotExist as e:
            self._delete_transaction(transaction)
            print('ERROR, object does not exist: {}'.format(str(e)))
            return ('ERROR, object does not exist', False, None)

            
        except Exception as e:
            self._delete_transaction(transaction)
            print('ERROR, creating share: {}'.format(str(e)))
            return ('Error creating share', False, None)


    def create_share_from_banktransaction(self, transaction, **kwargs):
        try:
            owner = Member.objects.get(id=kwargs['owner'])
            #Creating Share
            description = kwargs['description']
            if description == '':
                description = 'Share:{}- {}'.format(owner.get_full_name(), transaction.description)
                
            share = s_models.Share.objects.create(
                description = description,
                status = s_models.SHARE_STATUS[1][0],
                owner = owner,
                transaction=transaction,
            )

            return '',True, share

        except Exception as e:
            print('ERROR, creating share: {}'.format(str(e)))
            return ('Error creating share', False, None)

    def update_share(self, **kwargs):
        try:
            share = Share.objects.get(id=kwargs['id'])

            share.description = kwargs['description']
            share.save()

            return '', True, share

        except Share.DoesNotExist as e:
            print('ERROR, object does not exist: {}'.format(str(e)))
            return ('Error updating share', False, None)

        except Exception as e:
            print('ERROR, updating share: {}'.format(str(e)))
            return ('Error updating share', False, None)


    def delete_share(self, share):
        try:
            transaction = share.transaction

            transaction.reference.status = t_models.BANK_TRANSACTION_STATUS[0][0]
            transaction.reference.save()

            transaction.delete()

            share.delete()

            return ('', True, None)

        except Exception as e:
            return ('ERROR, deleting share transaction: {}'.format(str(e)),False, transaction)


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

    def _get_default_share_description(self, owner, bank_transaction):
        return 'Share: {}, {}'.format(owner.get_full_name(), bank_transaction.date_trans)
