
import factory
import factory.fuzzy as factory_fuzzy

from factory.django import DjangoModelFactory
import numpy as np
from datetime import datetime, timezone

from authentication.models import User
from members.models import Member
from transactions.models import Transaction, BankTransaction
from shares.models import Share
from savings.models import Saving
from expenses.models import Expense
from loans.models import Loan


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    email = factory.Faker('email')
    is_active = True


class MemberFactory(DjangoModelFactory):
    class Meta:
        model = Member

    is_active = True
    gender = factory_fuzzy.FuzzyChoice(['male', 'female'])
    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name_male') if gender == 'male' else factory.Faker('first_name_female')
    middle_name = factory.Faker('last_name') 
    last_name = factory.Faker('last_name')
    mobile_number = factory.Faker('msisdn')
    date_joined = datetime.now().replace(tzinfo=timezone.utc) #factory.LazyFunction(datetime.now().replace(tzinfo=timezone.utc))


class BankTransactionFactory(DjangoModelFactory):
    class Meta:
        model = BankTransaction 

    amount = factory.Faker('pyint', min_value=100000, max_value=1000000)
    description = factory.Faker('bothify',text='Transaction: ????-########', letters='ABCDE')
    balance = factory.Faker('pyint', min_value=10000000, max_value=100000000)
    status = 'imported'
    # date_trans = factory.Faker('date_between', start_date=datetime.date(2022,1,1), end_date=datetime.date(2022,3,1))
    date_trans = factory.Faker('date_between_dates', date_end=datetime(2022,3,10), date_start=datetime(2021,3,10))
    date_value = factory.Faker('date_between_dates', date_end=datetime(2022,3,10), date_start=datetime(2021,3,10))


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model=Transaction

class ShareFactory(DjangoModelFactory):
    class Meta:
        model=Share

class SavingFactory(DjangoModelFactory):
    class Meta:
        model=Saving

class ExpenseFactory(DjangoModelFactory):
    class Meta:
        model=Expense

class LoanFactory(DjangoModelFactory):
    class Meta:
        model = Loan
    
