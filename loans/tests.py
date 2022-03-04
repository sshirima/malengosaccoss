from django.test import TestCase, TransactionTestCase
from django.urls.base import reverse

from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
from loans.models import LoanFormFee, LoanInsuranceFee, LoanInterest, LoanLimits, LoanProcessingFee

from loans.services import LoanCRUDService
from transactions.services import BankStatementParserService
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
        print(loanrepayment)