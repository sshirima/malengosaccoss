from django.test import TestCase
from django.urls.base import reverse
from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
from loans.models import LoanFormFee, LoanInsuranceFee, LoanInterest, LoanLimits, LoanProcessingFee
from transactions.services import BankStatementParserService
from transactions.services import BankTransactionAssignmentService
# Create your tests here.

class TransactionTestCase(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('register'))
        self.valid_registration_form =  RegistrationForm(data={
            'first_name':'Samson',
            'last_name':'Shirima',
            'middle_name':'Stephen',
            'gender':'male',
            'email':'email@domain.com',
            'password1':'jimaya792',
            'password2':'jimaya792',
        })
        self.valid_registration_form.is_valid()
        registration_service = RegistrationService(self.response.wsgi_request)
        created, user = registration_service.create_user(self.valid_registration_form.cleaned_data)
        user.is_active = True
        user.is_staff = True
        user.save()

        self.user = user
        #Bank transactions
        parserService = BankStatementParserService()
        column_names = ['Tran Date', 'Value Date','Tran Particulars','Instrument\nId','Debit','Credit', 'Balance']
        df = parserService.parse_xlsx_file(filename='tests/statement_1.xlsx', column_names=column_names)
        message, created, qs = parserService.create_bank_transaction_db(df, column_names, self.user)
        self.banktransaction_qs = qs

    # def test_creating_transaction_success(self):
    #     TransactionCRUDService = TransactionCRUDService(self.response.wsgi_request)

    #     transactionCreateForm = TransactionCreateForm(data={
    #         'amount':10000.0,
    #         'reference':'ASDANKJADFS687676',
    #         'description':'Transaction descr',
    #     })

    #     is_valid = transactionCreateForm.is_valid()
    #     self.assertTrue(is_valid)

    #     (result, created, transaction) = TransactionCRUDService.create(transactionCreateForm.cleaned_data, self.user)

    #     self.assertTrue(created)
    #     self.assertIsNotNone(transaction)
    #     print(transaction)

    def test_assign_banktransaction_to_expense(self):
        banktransaction = self.banktransaction_qs[len(self.banktransaction_qs) -1]#qs[len(qs) -5]
        service = BankTransactionAssignmentService()
        msg, created, expense = service.assign_banktransaction_to_expense(banktransaction.id, created_by=self.user, description='')
        self.assertTrue(created)
        # from django.forms.models import model_to_dict
        # print(model_to_dict(expense))

    def test_assign_banktransaction_to_expense_multiple(self):
        banktransactions = self.banktransaction_qs[-3:]#qs[len(qs) -5]
        uuids = []
        for transaction in banktransactions:
            uuids.append(str(transaction.id))

        service = BankTransactionAssignmentService()
        msg, created, savings = service.assign_banktransactions_with_action(
            uuids, 
            action = 'assign_to_expenses',
            created_by=self.user, 
            description='', 
            owner=self.user.member.id
        )

        # self.assertTrue(created)
        self.assertEquals(3, len(savings))

    def test_assign_banktransaction_to_share_multiple(self):
        banktransactions = self.banktransaction_qs[:3]#qs[len(qs) -5]
        uuids = []
        for transaction in banktransactions:
            uuids.append(str(transaction.id))

        service = BankTransactionAssignmentService()
        msg, created, shares = service.assign_banktransactions_with_action(
            uuids, 
            action = 'assign_to_shares',
            created_by=self.user, 
            description='', 
            owner=self.user.member.id
        )

        self.assertTrue(created)
        self.assertEquals(3, len(shares))
    
    def test_assign_banktransaction_to_savings_multiple(self):
        banktransactions = self.banktransaction_qs[:3]#qs[len(qs) -5]
        uuids = []
        for transaction in banktransactions:
            uuids.append(str(transaction.id))

        service = BankTransactionAssignmentService()
        results = service.assign_banktransactions_with_action(
            uuids, 
            action = 'assign_to_savings',
            created_by=self.user, 
            description='', 
            owner=self.user.member.id
        )


        # self.assertTrue(created)
        self.assertEquals(3, len(results))

    def test_assign_banktransaction_to_share(self):
        banktransaction = self.banktransaction_qs[0]#qs[len(qs) -5]
        service = BankTransactionAssignmentService()
        msg, created, share = service.assign_banktransaction_to_share(banktransaction.id, created_by=self.user, description='', owner=self.user.member.id)
        self.assertTrue(created)
        banktransaction = self.banktransaction_qs[1]#qs[len(qs) -5]
        msg, created, share = service.assign_banktransaction_single_with_action('assign_to_shares', banktransaction.id, created_by=self.user, description='', owner=self.user.member.id)
        self.assertTrue(created)

    def test_assign_banktransaction_to_loan(self):
        banktransaction = self.banktransaction_qs[len(self.banktransaction_qs) -1]#qs[len(qs) -5]
        service = BankTransactionAssignmentService()

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
        
        msg, created, normal_loan = service.assign_banktransaction_to_loan(
            banktransaction.id, 
            created_by=self.user, 
            description='', 
            owner=self.user.member.id,
            status='avtive',
            loan_type = 'normal',
            duration = 6
        )

        LoanFormFee.objects.create(
            amount = 0,
            status='active',
            created_by = self.user,
            type='emergence'
        )

        LoanInterest.objects.create(
            percentage = 1,
            status='active',
            created_by = self.user, 
            type='emergence'
        )

        banktransaction = self.banktransaction_qs[len(self.banktransaction_qs) -4]
        msg, created, emergence_loan = service.assign_banktransaction_to_loan(
            banktransaction.id, 
            created_by=self.user, 
            description='', 
            owner=self.user.member.id,
            status='avtive',
            loan_type = 'emergence',
            duration = 1
        )

        banktransaction = self.banktransaction_qs[len(self.banktransaction_qs) -6]
        msg, created, loanrepayment = service.assign_banktransaction_to_loanrepayment(
            banktransaction.id, 
            created_by=self.user, 
            description='', 
            loan = normal_loan.id
        )

        banktransactions = self.banktransaction_qs[:3]#qs[len(qs) -5]
        uuids = []
        for transaction in banktransactions:
            uuids.append(str(transaction.id))

        service = BankTransactionAssignmentService()
        msg, created, shares = service.assign_banktransactions_with_action(
            uuids, 
            action = 'assign_to_loanrepayments',
            created_by=self.user, 
            description='', 
            owner=self.user.member.id,
            loan = normal_loan.id,
        )

        self.assertTrue(created)

    def test_assign_banktransaction_to_saving(self):
        banktransaction = self.banktransaction_qs[0]#qs[len(qs) -5]
        service = BankTransactionAssignmentService()
        msg, created, saving = service.assign_banktransaction_to_saving(
            banktransaction.id, 
            created_by=self.user, 
            description='', 
            owner=self.user.member.id
        )
        self.assertTrue(created)

    def test_get_transaction_assignment_action_by_type(self):
        type = 'credit'
        import transactions.models as m
        assignment_actions_by_type = m.get_transaction_assignment_action_by_type(type)
        assignment_actions_all = m.get_transaction_assignment_action_all()
        print(*assignment_actions_all)