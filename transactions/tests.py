import imp
from django.test import TestCase
from django.urls.base import reverse
from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
from transactions.forms import TransactionCreateForm
from transactions.services import BankStatementParserService, TransactionCRUDService
# Create your tests here.

class TransactionTestCase(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('register'))
        self.valid_registration_form =  RegistrationForm(data={
            'first_name':'Samson',
            'last_name':'Shirima',
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

    def test_bank_statement_parser(self):
        parserService = BankStatementParserService()

        column_names = ['Tran Date', 'Value Date','Tran Particulars','Instrument\nId','Debit','Credit', 'Balance']
        df = parserService.parse_xlsx_file(filename='tests/statement.xlsx', column_names=column_names)
        print(len(df.index))
        message, created, qs = parserService.create_bank_transaction_db(df, column_names, self.user)
        print(qs)
        