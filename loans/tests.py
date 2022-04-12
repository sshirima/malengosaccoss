from django.test import TestCase, TransactionTestCase
from django.urls.base import reverse

from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
from loans.models import LoanFormFee, LoanInsuranceFee, LoanInterest, LoanLimits, LoanProcessingFee

from loans.services import LoanCRUDService, LoanObject, LoanManager, LoanRepaymentManager
from transactions.models import BankTransaction
from transactions.services import BankStatementParserService, BankTransactionAssignmentService, TransactionCRUDService
from loans.forms import LoanCreateFromBankTransactionForm, LoanRepaymentCreateForm, LoanRepaymentMemberSelectForm
from members.models import Member

# Create your tests here.
class LoanTestCase(TransactionTestCase):

    def setUp(self):
        self.response = self.client.get(reverse('register'))
        self.valid_registration_form =  RegistrationForm(data={
            'first_name':'Samson',
            'last_name':'Shirima',
            'email':'email@domain.com',
            'password1':'jimaya792',
            'password2':'jimaya792',
            'gender':'male',
            'mobile_number': '255754710618',
            'middle_name':'Stephen'
        })
        self.valid_registration_form.is_valid()
        registration_service = RegistrationService(self.response.wsgi_request)
        created, user = registration_service.create_user(self.valid_registration_form.cleaned_data)
        user.is_active = True
        user.is_staff = True
        user.save()

        
        self.user = user

    def test_create_loan_from_banktransaction(self):
        #Parsing banktransactions
        parserService = BankStatementParserService()
        column_names = ['Tran Date', 'Value Date','Tran Particulars','Instrument\nId','Debit','Credit', 'Balance']
        df = parserService.parse_xlsx_file(filename='tests/statement_1.xlsx', column_names=column_names)
        message, created, qs = parserService.create_bank_transaction_db(df, column_names, self.user)
      
        banktransaction = qs[len(qs) -1]

        #Creating Loan
        loanservice = LoanCRUDService()

        #Set member active
        member = Member.objects.get(id=self.user.member.id)
        member.is_active = True
        member.save()

        valid_loan_create_form = LoanCreateFromBankTransactionForm(data={
            'duration':'6',
            'member':self.user.member.id,
            'loan_type':'normal',
            'transaction_id':banktransaction.id,
            'status':'issued',
        })

        LoanInterest.objects.create(
            percentage = 1.25,
            status='active',
            created_by = self.user
        )

        LoanInsuranceFee.objects.create(
            percentage = 1,
            status='active',
            created_by = self.user
        )

        LoanProcessingFee.objects.create(
            percentage = 1,
            status='active',
            created_by = self.user
        )

        LoanFormFee.objects.create(
            amount = 10000,
            status='active',
            created_by = self.user
        )

        LoanLimits.objects.create(
            type = 'normal',
            max_principle= 12000000,
            max_duration = 12,
            status='active',
            created_by = self.user
        )

        is_valid_form = valid_loan_create_form.is_valid()
        print(valid_loan_create_form.errors)
        self.assertTrue(is_valid_form)
        
        msg, created, loan = loanservice.create_loan(data=valid_loan_create_form.cleaned_data, creator=self.user)

        self.assertTrue(created)
        self.assertIsNotNone(loan)

        #Testing loanpayment creatiion
        form_select = LoanRepaymentMemberSelectForm(data={
            'member':self.user.member.id
        })

        is_valid_form_select = form_select.is_valid()
        self.assertTrue(is_valid_form_select)

        transaction = qs[len(qs) -5]

        form_create_loanrepayment = LoanRepaymentCreateForm(data={
            'loan':loan.id,
            'transaction':transaction.id
        })

        is_valid = form_create_loanrepayment.is_valid()
        self.assertTrue(is_valid)

        msg, created, loanrepayment = loanservice.create_loan_repaymet(data=form_create_loanrepayment.cleaned_data, creator=self.user)

        self.assertTrue(created)

        """+++++++++++++++++++++++++++++++++++++++++++++++++++"""

        loanobject = LoanObject()
        loanobject.load(loan)
        self.assertEquals(loan.principle, loanobject.principle)

        loanObject2 = LoanObject(loan.id)
        self.assertEquals(loan.principle, loanObject2.principle)


        """
        testing creating object from user request
        """
        loanObject3 = LoanObject()
        loanObject3.create_new_loan_from_request(
            principle= 1000000,
            time = 10,
            type = 'normal',
            member = member.id
        )
        self.assertEquals(loanObject3.principle, 1000000)
        self.assertEquals(loanObject3.interest_amount, 135000)
        self.assertEquals(loanObject3.amount_issued, 970000)
        self.assertEquals(loanObject3.installment_amount, 113500)

        # loanObject3.save_loan_details(created_by=self.user)

        loan_manager = LoanManager(loanObject3)
        is_qualified = loan_manager.qualify_member_loan()
        self.assertFalse(is_qualified)

        paid_loan = BankTransaction.objects.create(
            amount=970000,
            description = 'Description',
            balance=300000,
            type='debit',
            status='imported',
            date_trans = '2021-05-11',
            date_value = '2021-05-11',
            created_by = self.user
        )

        loanObject4 = LoanObject()
        msg, created, loan = loanObject4.create_new_loan_from_amount_issued(
            banktransaction= paid_loan,
            time = 10,
            type = 'normal',
            member = member.id,
            created_by = self.user
        )
        self.assertTrue(created)
        self.assertEquals(loanObject4.principle, 1000000)
        self.assertEquals(loanObject4.interest_amount, 135000)
        self.assertEquals(loanObject4.installment_amount, 113500)

        """
        Creating testing savings for the member
        """
        for _ in range(3):
            paid_saving = BankTransaction.objects.create(
                amount=200000,
                description = '',
                balance=300000,
                type='credit',
                status='imported',
                date_trans = '2021-05-11',
                date_value = '2021-05-11',
                created_by = self.user
            )
            service = BankTransactionAssignmentService()
            msg, created, saving = service.assign_banktransaction_to_saving(
                paid_saving.id, 
                created_by=self.user, 
                description='', 
                owner=member.id
            )
        """
        Creatinng testing shares to member
        """

        for _ in range(3):
            paid_saving = BankTransaction.objects.create(
                amount=50000,
                description = '',
                balance=300000,
                type='credit',
                status='imported',
                date_trans = '2021-10-11',
                date_value = '2021-10-11',
                created_by = self.user
            )
            service = BankTransactionAssignmentService()
            msg, created, saving = service.assign_banktransaction_to_share(
                paid_saving.id, 
                created_by=self.user, 
                description='', 
                owner=member.id
            )

        loan_manager2 = LoanManager(loanObject4)
        is_qualified = loan_manager2.qualify_member_loan()
        self.assertTrue(is_qualified)

        """
            Testing loan repayment besiness logic
        """
        loanpayment = BankTransaction.objects.create(
                amount=100000,
                description = '',
                balance=300000,
                type='credit',
                status='imported',
                date_trans = '2022-02-11',
                date_value = '2022-02-11',
                created_by = self.user
            )

        msg, created , principle_pay, interest_pay = loan_manager2.receive_loan_repayment_transaction(loanpayment, created_by = self.user)
        
        self.assertTrue(created)

        first_payment_date = loan_manager2.get_loan_first_payment_deadline()
        nth_payment_deadline = loan_manager2.get_nth_payment_deadline(5)
        nth_installment_principle_total = loan_manager2.get_nth_installment_principle_total(2)
        nth_installment_interest_total = loan_manager2.get_nth_installment_interest_total(2)
        date_difference_in_months = loan_manager2.get_date_difference_in_months(first_payment_date)

        # self.assertEquals(str(first_payment_date), '2022-02-05')
        # self.assertEquals(str(nth_payment_deadline), '2022-06-05')
        self.assertEquals(nth_installment_principle_total, 200000)
        self.assertEquals(nth_installment_interest_total, 27000)
        print(str(first_payment_date))
        print(str(nth_payment_deadline))
        print(str(nth_installment_principle_total))
        print(str(nth_installment_interest_total))
        print(str(date_difference_in_months))
        print(principle_pay.amount)
        print(interest_pay.amount)

