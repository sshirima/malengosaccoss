import traceback
from django.core.exceptions import ObjectDoesNotExist
from members.models import Member

from transactions.models import BankTransaction, Transaction
import transactions.models as t_models
from loans.models import Loan, LoanFormFee, LoanInsuranceFee, LoanInterest, LoanProcessingFee, LoanRepayment



class LoanCRUDService():

    def create_loan(self, data, creator):
        try:
            bankTransaction = BankTransaction.objects.get(id=data['transaction_id'])

            #create transaction
            transaction = Transaction.objects.create(
                    amount= bankTransaction.amount, 
                    description=bankTransaction.description,
                    reference=bankTransaction, 
                    type=bankTransaction.type,
                    status= t_models.TRANSACTION_STATUS[1][0],
                    created_by = creator
            )

            #Member Id
            member = Member.objects.get(id=data['member'])

            #Get FormFee
            form_fee = LoanFormFee.objects.filter(status='active', type=data['loan_type']).latest('date_created')

            #Get Interest
            interest = LoanInterest.objects.filter(status='active', type=data['loan_type']).latest('date_created')

            #Get LoanFormFee
            loanprocessing = LoanProcessingFee.objects.filter(status='active').latest('date_created')

            #Get LoanInsuranceFee
            insurance = LoanInsuranceFee.objects.filter(status='active').latest('date_created')

            #Calculate Principle
            principle = ((bankTransaction.amount + form_fee.amount)*100)/98#((bankTransaction.amount + form_fee.amount)*100)/98

            #Calculate forminsurance
            insurance_fee = principle * (insurance.percentage/100)

            #Calculate loanfee
            loan_fee = principle * (loanprocessing.percentage/100)

            #RepaidAmount
            duration = int(data['duration'])
            interest_amount = (principle*(1+ (interest.percentage*duration)))/100

            #Monthly installment
            installment_amount = (principle + interest_amount)/duration

            #form fee amount

            loan = Loan.objects.create(
                type = data['loan_type'],
                principle = principle,
                duration = duration,
                interest_rate = interest.percentage,
                status = 'issued',
                member = member,
                amount_issued = bankTransaction.amount,
                loan_fee = loan_fee,
                insurance_fee = insurance_fee,
                form_fee = form_fee.amount,
                interest_amount = interest_amount,
                transaction = transaction,
                installment_amount = installment_amount,
                created_by = creator
            )

            #Mark bank transactions as issued
            self._change_bank_transaction_status(bankTransaction, t_models.BANK_TRANSACTION_STATUS[1][0])

            return ('', True, loan)

        except ObjectDoesNotExist as e:
            print('ERROR, object not found: {}'.format(str(e)))
            #Delete Transaction
            if transaction:
                transaction.delete()
            return ('Object does not exist', False, None)

        except Exception as e:
            traceback.print_exc()
            #Delete Transaction
            if transaction:
                transaction.delete()
            return ('error creating loan from bank transaction', False, None)

    def create_loan_repaymet(self, data, creator):

        try:
            bankTransaction = BankTransaction.objects.get(id=data['transaction'])

            if bankTransaction.status == 'assigned':
                return 'Transaction already assigned', False, None

            #Member Id
            loan = Loan.objects.get(id=data['loan'])

            #create transaction
            transaction = Transaction.objects.create(
                    amount= bankTransaction.amount, 
                    description=bankTransaction.description,
                    reference=bankTransaction, 
                    type=bankTransaction.type,
                    status= t_models.TRANSACTION_STATUS[1][0],
                    created_by = creator
            )

            loanrepayment = LoanRepayment.objects.create(
                loan= loan,
                transaction = transaction,
                created_by = creator,
            )

            #Mark bank transactions as issued
            self._change_bank_transaction_status(bankTransaction, t_models.BANK_TRANSACTION_STATUS[1][0])

            return '', True, loanrepayment

        except ObjectDoesNotExist as e:
            print('ERROR, object not found: {}'.format(str(e)))
            #Delete Transaction
            if transaction:
                transaction.delete()
            return ('Object does not exist', False, None)

        except Exception as e:
            traceback.print_exc()
            #Delete Transaction
            if transaction:
                transaction.delete()
            return ('Error creating loan repayment', False, None)

    def create_loanrepayment_from_transaction(self, transaction, **kwargs):
        try:
            #Member Id
            loan = Loan.objects.get(id=kwargs['loan'])

            loanrepayment = LoanRepayment.objects.create(
                loan= loan,
                transaction = transaction,
                created_by = kwargs['created_by'],
            )

            return '', True, loanrepayment

        except Exception as e:
            print('Error creating loan repayment:{}'.format(str(e)))
            return ('Error creating loan repayment', False, None)

    def create_loan_from_transaction(self, transaction, **kwargs):
        try:
            #Member Id
            member = Member.objects.get(id=kwargs['member'])

            #Get FormFee
            form_fee = LoanFormFee.objects.filter(status='active', type=kwargs['loan_type']).latest('date_created')

            #Get Interest
            interest = LoanInterest.objects.filter(status='active', type=kwargs['loan_type']).latest('date_created')

            #Get LoanFormFee
            loanprocessing = LoanProcessingFee.objects.filter(status='active').latest('date_created')

            #Get LoanInsuranceFee
            insurance = LoanInsuranceFee.objects.filter(status='active').latest('date_created')

            #Calculate Principle
            principle = ((transaction.amount + form_fee.amount)*100)/98#((bankTransaction.amount + form_fee.amount)*100)/98

            #Calculate forminsurance
            insurance_fee = principle * (insurance.percentage/100)

            #Calculate loanfee
            loan_fee = principle * (loanprocessing.percentage/100)

            #RepaidAmount
            duration = int(kwargs['duration'])
            interest_amount = (principle*(1+ (interest.percentage*duration)))/100

            #Monthly installment
            installment_amount = (principle + interest_amount)/duration

            #form fee amount

            loan = Loan.objects.create(
                type = kwargs['loan_type'],
                principle = principle,
                duration = duration,
                interest_rate = interest.percentage,
                status = 'issued',
                member = member,
                amount_issued = transaction.amount,
                loan_fee = loan_fee,
                insurance_fee = insurance_fee,
                form_fee = form_fee.amount,
                interest_amount = interest_amount,
                transaction = transaction,
                installment_amount = installment_amount,
                created_by = kwargs['created_by']
            )

            return '', True, loan

        except Exception as e:
            print('Error creating loan : {}'.format(str(e)))
            return ('Error creating loan', False, None)
    def _change_bank_transaction_status(self, bank_transaction, status):

        if bank_transaction:
            bank_transaction.status = status
            bank_transaction.save()
            return True

        return False
        