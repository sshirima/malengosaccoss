import imp
from django.test import TestCase
from django.urls.base import reverse
from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
from transactions.forms import TransactionCreateForm
from transactions.services import BankStatementParserService, TransactionCRUDService
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

    # def test_assign_banktransaction_to_expense_multiple(self):
    #     banktransactions = self.banktransaction_qs[-3:]#qs[len(qs) -5]
    #     uuids = []
    #     for transaction in banktransactions:
    #         uuids.append(str(transaction.id))

    #     service = BankTransactionAssignmentService()
    #     msg, created, expenses = service.assign_banktransaction_to_expense_multiple(uuids, created_by=self.user, description='')
    #     self.assertTrue(created)
    #     self.assertEquals(3, len(expenses))

    # def test_assign_banktransaction_to_share_multiple(self):
    #     banktransactions = self.banktransaction_qs[:3]#qs[len(qs) -5]
    #     uuids = []
    #     for transaction in banktransactions:
    #         uuids.append(str(transaction.id))

    #     service = BankTransactionAssignmentService()
    #     msg, created, shares = service.assign_banktransaction_to_share_multiple(uuids, created_by=self.user, description='', owner=self.user.member.id)
    #     self.assertTrue(created)
    #     self.assertEquals(3, len(shares))


    def test_assign_banktransaction_to_share(self):
        banktransaction = self.banktransaction_qs[0]#qs[len(qs) -5]
        service = BankTransactionAssignmentService()
        msg, created, share = service.assign_banktransaction_to_share(banktransaction.id, created_by=self.user, description='', owner=self.user.member.id)
        self.assertTrue(created)


    def test_get_transaction_assignment_action_by_type(self):
        type = 'credit'
        import transactions.models as m
        assignment_actions_by_type = m.get_transaction_assignment_action_by_type(type)
        assignment_actions_all = m.get_transaction_assignment_action_all()
        