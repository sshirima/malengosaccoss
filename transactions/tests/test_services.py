from fileinput import filename
from django.test import TestCase
from django.urls.base import reverse
from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
from transactions.models import BankStatement
from transactions.services import BankStatementParserService
from core.utils import get_timestamps_filename
from datetime import datetime

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
        created, user = registration_service.create_user(**self.valid_registration_form.cleaned_data)
        user.is_active = True
        user.is_staff = True
        user.save()
        self.user = user
        #Bank transactions
    
    """
    Test bank statement parser
    """

    def test_bankstatement_parser(self):
        file_name = get_timestamps_filename(datetime.now(), 'statement_1.xlsx')
        parserService = BankStatementParserService()
        column_names = ['Tran Date', 'Value Date','Tran Particulars','Instrument\nId','Debit','Credit', 'Balance']
        df = parserService.parse_xlsx_file(filename='tests/statement_1.xlsx', column_names=column_names)
        message, created, qs = parserService.create_bank_transaction_db(df, column_names, self.user, filename=file_name)
        self.banktransaction_qs = qs
        bankstatement = BankStatement.objects.get(filename=file_name)
        self.assertEqual(bankstatement.filename, file_name)