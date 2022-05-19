import traceback
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from members.models import Member
from transactions.models import BankTransaction, Transaction
import transactions.models as t_models
from loans.models import Loan, LoanFormFee, LoanInsuranceFee, LoanInterest, LoanProcessingFee, LoanRepayment
from shares.models import Share
from savings.models import Saving
from transactions.services import TransactionCRUDService


# class LoanCRUDService(): 


    # def create_loan(self, data, creator):
    #     try:
    #         bankTransaction = BankTransaction.objects.get(id=data['transaction_id'])

    #         #create transaction
    #         transaction = Transaction.objects.create(
    #                 amount= bankTransaction.amount, 
    #                 description=bankTransaction.description,
    #                 reference=bankTransaction, 
    #                 type=bankTransaction.type,
    #                 status= t_models.TRANSACTION_STATUS[1][0],
    #                 created_by = creator
    #         )

    #         #Member Id
    #         member = Member.objects.get(id=data['member'])

    #         #Get FormFee
    #         form_fee = LoanFormFee.objects.filter(status='active', type=data['loan_type']).latest('date_created')

    #         #Get Interest
    #         interest = LoanInterest.objects.filter(status='active', type=data['loan_type']).latest('date_created')

    #         #Get LoanFormFee
    #         loanprocessing = LoanProcessingFee.objects.filter(status='active').latest('date_created')

    #         #Get LoanInsuranceFee
    #         insurance = LoanInsuranceFee.objects.filter(status='active').latest('date_created')

    #         #Calculate Principle
    #         principle = ((bankTransaction.amount + form_fee.amount)*100)/98#((bankTransaction.amount + form_fee.amount)*100)/98

    #         #Calculate forminsurance
    #         insurance_fee = principle * (insurance.percentage/100)

    #         #Calculate loanfee
    #         loan_fee = principle * (loanprocessing.percentage/100)

    #         #RepaidAmount
    #         duration = int(data['duration'])
    #         interest_amount = (principle*(1+ (interest.percentage*duration)))/100

    #         #Monthly installment
    #         installment_amount = (principle + interest_amount)/duration

    #         #form fee amount

    #         loan = Loan.objects.create(
    #             type = data['loan_type'],
    #             principle = principle,
    #             duration = duration,
    #             interest_rate = interest.percentage,
    #             status = 'issued',
    #             member = member,
    #             amount_issued = bankTransaction.amount,
    #             loan_fee = loan_fee,
    #             insurance_fee = insurance_fee,
    #             form_fee = form_fee.amount,
    #             interest_amount = interest_amount,
    #             transaction = transaction,
    #             installment_amount = installment_amount,
    #             created_by = creator
    #         )

    #         #Mark bank transactions as issued
    #         self._change_bank_transaction_status(bankTransaction, t_models.BANK_TRANSACTION_STATUS[1][0])

    #         return ('', True, loan)

    #     except ObjectDoesNotExist as e:
    #         print('ERROR, object not found: {}'.format(str(e)))
    #         #Delete Transaction
    #         if transaction:
    #             transaction.delete()
    #         return ('Object does not exist', False, None)

    #     except Exception as e:
    #         traceback.print_exc()
    #         #Delete Transaction
    #         if transaction:
    #             transaction.delete()
    #         return ('error creating loan from bank transaction', False, None)

    # def create_loan_repaymet(self, data, creator):

    #     try:
    #         bankTransaction = BankTransaction.objects.get(id=data['transaction'])

    #         if bankTransaction.status == 'assigned':
    #             return 'Transaction already assigned', False, None

    #         #Member Id
    #         loan = Loan.objects.get(id=data['loan'])

    #         #create transaction
    #         transaction = Transaction.objects.create(
    #                 amount= bankTransaction.amount, 
    #                 description=bankTransaction.description,
    #                 reference=bankTransaction, 
    #                 type=bankTransaction.type,
    #                 status= t_models.TRANSACTION_STATUS[1][0],
    #                 created_by = creator
    #         )

    #         loanrepayment = LoanRepayment.objects.create(
    #             loan= loan,
    #             transaction = transaction,
    #             created_by = creator,
    #         )

    #         #Mark bank transactions as issued
    #         self._change_bank_transaction_status(bankTransaction, t_models.BANK_TRANSACTION_STATUS[1][0])

    #         return '', True, loanrepayment

    #     except ObjectDoesNotExist as e:
    #         print('ERROR, object not found: {}'.format(str(e)))
    #         #Delete Transaction
    #         if transaction:
    #             transaction.delete()
    #         return ('Object does not exist', False, None)

    #     except Exception as e:
    #         traceback.print_exc()
    #         #Delete Transaction
    #         if transaction:
    #             transaction.delete()
    #         return ('Error creating loan repayment', False, None)

    # def create_loanrepayment_from_transaction(self, transaction, **kwargs):
    #     try:
    #         #Member Id
    #         loan = Loan.objects.get(id=kwargs['loan'])

    #         loanrepayment = LoanRepayment.objects.create(
    #             loan= loan,
    #             transaction = transaction,
    #             created_by = kwargs['created_by'],
    #         )

    #         return '', True, loanrepayment

    #     except Exception as e:
    #         print('Error creating loan repayment:{}'.format(str(e)))
    #         return ('Error creating loan repayment', False, None)

    # def create_loan_from_transaction(self, transaction, **kwargs):
    #     try:
    #         #Member Id
    #         member = Member.objects.get(id=kwargs['owner'])

    #         #Get FormFee
    #         form_fee = LoanFormFee.objects.filter(status='active', type=kwargs['loan_type']).latest('date_created')

    #         #Get Interest
    #         interest = LoanInterest.objects.filter(status='active', type=kwargs['loan_type']).latest('date_created')

    #         #Get LoanFormFee
    #         loanprocessing = LoanProcessingFee.objects.filter(status='active').latest('date_created')

    #         #Get LoanInsuranceFee
    #         insurance = LoanInsuranceFee.objects.filter(status='active').latest('date_created')

    #         #Calculate Principle
    #         principle = ((transaction.amount + form_fee.amount)*100)/98#((bankTransaction.amount + form_fee.amount)*100)/98

    #         #Calculate forminsurance
    #         insurance_fee = principle * (insurance.percentage/100)

    #         #Calculate loanfee
    #         loan_fee = principle * (loanprocessing.percentage/100)

    #         #RepaidAmount
    #         duration = int(kwargs['duration'])
    #         interest_amount = (principle*(1+ (interest.percentage*duration)))/100

    #         #Monthly installment
    #         installment_amount = (principle + interest_amount)/duration

    #         #form fee amount

    #         loan = Loan.objects.create(
    #             type = kwargs['loan_type'],
    #             principle = principle,
    #             duration = duration,
    #             interest_rate = interest.percentage,
    #             status = 'issued',
    #             member = member,
    #             amount_issued = transaction.amount,
    #             loan_fee = loan_fee,
    #             insurance_fee = insurance_fee,
    #             form_fee = form_fee.amount,
    #             interest_amount = interest_amount,
    #             transaction = transaction,
    #             installment_amount = installment_amount,
    #             created_by = kwargs['created_by']
    #         )

    #         return '', True, loan

    #     except Exception as e:
    #         print('Error creating loan : {}'.format(str(e)))
    #         return ('Error creating loan', False, None)


    # def calculate_interest_amount(self, p, r, t):
    #     return (p*(1+ (r*t)))/100

    # def _change_bank_transaction_status(self, bank_transaction, status):

    #     if bank_transaction:
    #         bank_transaction.status = status
    #         bank_transaction.save()
    #         return True

    #     return False


class LoanObject():
    principle = None
    rate = None
    time = None
    member = None
    amount_issued = None
    form_fee = None
    insurance_fee = None
    processing_fee = None
    date_issued = None
    interest_amount = None
    installment_amount = None
    type = None
    transaction = None
    model = None
    loan_repayments = None

    def __init__(self, id = None, loan = None):

        if loan is not None:
            #Load loan properties
            self.load(loan)
            self.model = loan

            #Loan loan repayemnts
            self.load_repayments()

        if id is not None:
            loan = Loan.objects.select_related('member', 'transaction__reference').get(id=id)

            if loan:
                #Load loan properties
                self.load(loan)
                self.model = loan

                #Loan loan repayemnts
                self.load_repayments()

    def load(self, loan):
        try:
            self.principle = loan.principle
            self.rate = loan.interest_rate
            self.time = loan.duration
            self.member = loan.member
            self.date_issued = loan.transaction.reference.date_trans
            self.amount_issued = loan.amount_issued
            self.type = loan.type
            self.insurance_fee = loan.insurance_fee
            self.form_fee = loan.form_fee
            self.processing_fee = loan.loan_fee
            self.transaction = loan.transaction
            self.installment_amount = loan.installment_amount
            self.interest_amount = loan.interest_amount

        except Exception as e:
            msg = 'Error, loading loan from loan model: {}, {}'.format(e.__traceback__.tb_lineno, str(e))
            print(msg)

    def load_repayments(self):
        self.loan_repayments = LoanRepayment.objects.filter(loan = self.model)

    def get_sum_loan_repayments(self):
        
        return self.loan_repayments.aggregate(Sum('transaction__amount'))['transaction__amount__sum']

    def get_sum_loan_repayments_principle(self):
        
        return self.loan_repayments.aggregate(Sum('principle_amount'))['principle_amount__sum']

    def get_sum_loan_repayments_interest(self):
        
        return self.loan_repayments.aggregate(Sum('interest_amount'))['interest_amount__sum']

    def get_outstanding_balance(self):
        
        return self.principle - float(self.get_sum_loan_repayments_principle())

    def create_new_loan_from_request(self, **kwargs):
        try:
            self.principle = kwargs.pop('principle', None)
            self.time = kwargs.pop('time', None)
            self.type = kwargs.pop('type', None)
            member_id = kwargs.pop('member', None)
            self.rate = self.get_current_interest_rate()
            #Configured values
            processing_rate = self.get_current_processing_rate()
            insurance_rate = self.get_current_insurance_rate()
            

            #Calculted values
            self.processing_fee = self.calculate_processing_fee(processing_rate)
            self.insurance_fee = self.calculate_insurance_fee(insurance_rate)
            self.interest_amount = self.calculate_interest_amount()
            self.form_fee = self.get_current_form_fee()
            self.member = self.get_member(member_id)
            self.installment_amount = self.calculate_installment_amount()
            self.amount_issued = self.calculate_amount_issued()

        except Exception as e:
            msg = 'Error, creating new loan from request: line {}, {}'.format(e.__traceback__.tb_lineno, str(e))
            print(msg)

    def create_new_loan_from_amount_issued(self, **kwargs):
        try:
            banktransaction = kwargs.pop('banktransaction', None)
            self.amount_issued = banktransaction.amount
            self.time = kwargs.pop('time', None)
            self.type = kwargs.pop('type', None)
            member_id = kwargs.pop('member', None)
            self.form_fee = self.get_current_form_fee()
            self.rate = self.get_current_interest_rate()
            self.principle = self.calculate_principle_from_issued_amount()
            #Configured values
            
            processing_rate = self.get_current_processing_rate()
            insurance_rate = self.get_current_insurance_rate()

            #Calculted values
            self.processing_fee = self.calculate_processing_fee(processing_rate)
            self.insurance_fee = self.calculate_insurance_fee(insurance_rate)
            self.interest_amount = self.calculate_interest_amount()
            self.member = self.get_member(member_id)
            self.installment_amount = self.calculate_installment_amount()
            self.amount_issued = self.calculate_amount_issued()
            
            transaction_crud = TransactionCRUDService()
            msg,cr,bt,t = transaction_crud.create_transaction_from_banktransaction(banktransaction.id, created_by=kwargs['created_by'])
            self.transaction = t
            return self.save_loan_details(created_by=kwargs['created_by'])
        

        except Exception as e:
            msg = 'Error, creating new loan from amount issued,file {}, line {}: {}'.format(e.__traceback__.tb_frame.f_code.co_filename, e.__traceback__.tb_lineno, str(e))
            print(msg)
            return msg, False, None

    def save_loan_details(self, **kwargs):
        try:
            loan = Loan.objects.create(
                type = self.type,
                principle = self.principle,
                duration = self.time,
                interest_rate = self.rate,
                status = 'issued',
                member = self.member,
                amount_issued = self.amount_issued,
                loan_fee = self.processing_fee,
                insurance_fee = self.insurance_fee,
                form_fee = self.form_fee,
                interest_amount = self.interest_amount,
                transaction = self.transaction,
                installment_amount = self.installment_amount,
                created_by = kwargs['created_by']
            )
            self.model = loan
            return '', True, loan

        except Exception as e:
            msg = 'Error, saving loan details: {}, {}'.format(e.__traceback__.tb_lineno, str(e))
            print(msg)
            return msg, False, None

    def calculate_amount_issued(self):
        return self.principle - self.form_fee - self.insurance_fee - self.processing_fee

    def calculate_principle_from_issued_amount(self):
        return ((self.amount_issued + self.form_fee)*100)/98

    def calculate_interest_amount(self):
        
        return (self.principle*(1+ (self.rate*self.time)))/100

    def calculate_insurance_fee(self, insurance_rate):
        return self.principle * (insurance_rate/100)

    def calculate_processing_fee(self, processing_rate):
        return self.principle * (processing_rate/100)

    def calculate_installment_amount(self):
        return (self.principle + self.interest_amount)/self.time

    def get_member(self, id):
        return Member.objects.get(id=id)

    def get_current_interest_rate(self):
        return LoanInterest.objects.filter(status='active', type=self.type).latest('date_created').percentage

    def get_current_form_fee(self):
        return LoanFormFee.objects.filter(status='active', type=self.type).latest('date_created').amount

    def get_current_processing_rate(self):
        return LoanProcessingFee.objects.filter(status='active').latest('date_created').percentage

    def get_current_insurance_rate(self):
        return LoanInsuranceFee.objects.filter(status='active').latest('date_created').percentage


class LoanManager():
    loan = None
    SAVINGS_LOAN_FACTOR = 3
    SHARES_LOAN_FACTOR = 10

    def __init__(self, loan) -> None:
        self.loan = loan

    def qualify_member_loan(self):
        try:
            total_shares = Share.objects.filter(owner=self.loan.member).aggregate(total=Sum('transaction__reference__amount'))['total']
            total_saving = Saving.objects.filter(owner=self.loan.member).aggregate(total=Sum('transaction__reference__amount'))['total']

            total_shares = 0 if total_shares is None else total_shares
            total_saving = 0 if total_saving is None else total_saving
            
            required_savings = total_saving * self.SAVINGS_LOAN_FACTOR
            required_shares = total_shares * self.SHARES_LOAN_FACTOR

            if self.loan.principle > required_savings or self.loan.principle > required_shares:
                return False

            return True

        except Exception as e:
            msg = 'Error,  Qualifying member loan: {}, {}'.format(e.__traceback__.tb_lineno, str(e))
            print(msg)
            return msg, False

    def pay_loan(self, banktransaction, **kwargs):
        #Calculate interest payment
        try:
            transaction_crud = TransactionCRUDService()
            msg,created,banktransaction,transaction = transaction_crud.create_transaction_from_banktransaction(banktransaction.id, created_by=kwargs['created_by'])
            interest_pay = self.calculate_interest_monthly_installment_amount()
            principle_pay = self.calculate_principle_pay(interest_pay, transaction.reference.amount)

            return self.save_repayment_details(interest_pay, principle_pay, transaction=transaction)

        except Exception as e:
            msg = 'Error,  receiving loan repayment transaction: {}, {}'.format(e.__traceback__.tb_lineno, str(e))
            print(msg)
            return msg, False, None, None

    def get_loan_first_payment_deadline(self):

        date = self.loan.model.transaction.reference.date_trans

        next_paying_date = date + timedelta(days=31) + relativedelta(months=1)

        return next_paying_date.replace(day=5)

    def get_date_difference_in_months(self, from_date, to_date=datetime.now()):
        r = relativedelta(to_date, from_date)
        return (r.years * 12) + r.months

    def get_nth_payment_deadline(self, nth):
        first_payment_deadline = self.get_loan_first_payment_deadline()
        
        if not (nth > 0) or not (nth <= self.loan.time):
            return None
        
        nth = nth - 1
        nth_payment_deadline = first_payment_deadline + relativedelta(months=nth)
        return nth_payment_deadline

    def get_nth_installment_principle_total(self, nth):
        p_repayment = self.calculate_principle_monthly_installment_amount()

        if not (nth > 0) or not (nth <= self.loan.time) :
            return None

        return p_repayment*nth

    def get_nth_installment_interest_total(self, nth):
        i_repayment = self.calculate_interest_monthly_installment_amount()

        if not (nth > 0) or not (nth < self.loan.time) :
            return None

        return i_repayment*nth

    def calculate_principle_monthly_installment_amount(self):
        return self.loan.principle/self.loan.time

    def calculate_interest_monthly_installment_amount(self):
        return self.loan.interest_amount/self.loan.time

    def calculate_principle_pay(self, interest_pay, total_payment):
        return total_payment-interest_pay if total_payment-interest_pay > 0 else 0

    def save_repayment_details(self, interest_pay, principle_pay, **kwargs):
        try:
            loan_repayment = LoanRepayment.objects.create(
                loan = self.loan.model,
                transaction = kwargs['transaction'],
                principle_amount = principle_pay,
                interest_amount = interest_pay
            )

            return '', True , loan_repayment

        except Exception as e:
            msg = 'Error, saving loan repayment details: {}, {}'.format(e.__traceback__.tb_lineno, str(e))
            print(msg)
            return msg, False , None, None
    