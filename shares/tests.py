from django.test import TestCase
from members.models import Member
from shares.services import ShareCrudService

from transactions.models import BankTransaction
from transactions.services import BankTransactionAssignmentService
from .forms import ShareAuthorizationForm, ShareCreateForm
from authentication.models import User
from django.urls.base import reverse
from authentication.forms import RegistrationForm
from authentication.services import RegistrationService
# Create your tests here.


class ShareFormsTest(TestCase):
    

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

    def test_share_create_success(self):
        member = Member.objects.get(id=self.user.member.id)
        member.is_active = True
        member.save()

        bank_transaction = BankTransaction.objects.create(
            amount=20000,
            description = 'Description',
            balance=300000,
            type='credit',
            status='imported',
            date_trans = '2021-10-11',
            date_value = '2021-10-11',
            created_by = self.user
        )

        share_create_form = ShareCreateForm(data={
            'type':'credit',
            'status':'approved',
            'description':'Share description',
            'reference':bank_transaction.id,
            'owner':member.id
        })
        is_valid = share_create_form.is_valid()
        print(share_create_form.errors)
        self.assertTrue(is_valid)
        
        service = BankTransactionAssignmentService()
        msg, created, saving = service.assign_banktransaction_to_share(
            bank_transaction.id, 
            created_by=self.user, 
            description='', 
            owner=member.id
        )
        self.assertTrue(created)
        self.assertIsNotNone(saving)