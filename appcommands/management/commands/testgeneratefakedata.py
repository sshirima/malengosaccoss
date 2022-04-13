import random

from django.db import transaction
from django.core.management.base import BaseCommand
import factory
from django.db.models import Sum

from tests.factory.factories import (
    BankTransactionFactory,
    LoanFactory, 
    SavingFactory, 
    ShareFactory, 
    TransactionFactory, 
    UserFactory, 
    MemberFactory,
    ExpenseFactory
)
from authentication.models import User
from members.models import Member
from transactions.models import BankTransaction

NUMBER_USERS = 50
NUMBER_SHARES = 500
NUMBER_SAVINGS = 500
NUMBER_EXPENSE = 100
NUMBER_LOAN = 100


class Command(BaseCommand):
    help = "Generate test data ..."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Generating fake data to database....')

        #Creating fake users
        self.stdout.write('Generating fake users....')
        users = []
        for _ in range(NUMBER_USERS):
            user = UserFactory()
            user.set_password('jimaya792')
            user.save()
            users.append(user)

        #Creating fake members
        self.stdout.write('Generating fake members....')
        members = []
        for user in users:
            member = MemberFactory(user=user)
            members.append(member)

        
        adminuser = User.objects.get(email = 'admin@localhost.com')
        

        #Generating shares 
        self.stdout.write('Generating fake shares....')
        share_banktransaction = self.generate_fake_banktransactions(NUMBER_SHARES, created_by= adminuser, type='credit')
        share_transactions = self.generate_fake_transactions(share_banktransaction, created_by=adminuser)
        shares = self.generate_fake_shares(share_transactions, members)

        #Generating savings
        self.stdout.write('Generating fake savings....')
        saving_banktransaction = self.generate_fake_banktransactions(NUMBER_SAVINGS, created_by= adminuser, type='credit')
        saving_transactions = self.generate_fake_transactions(saving_banktransaction, created_by=adminuser)
        savings = self.generate_fake_savings(saving_transactions, members)

        #Generating expenses
        self.stdout.write('Generating fake expenses....')
        saving_banktransaction = self.generate_fake_banktransactions(
            NUMBER_SAVINGS, 
            created_by= adminuser, 
            type='debit',
            amount = factory.Faker('pyint', min_value=1000 , max_value=10000),
        )
        expenses_transactions = self.generate_fake_transactions(saving_banktransaction, created_by=adminuser)
        expenses = self.generate_fake_expenses(expenses_transactions)

        #Generating loans
        self.stdout.write('Generating fake loans....')
        bankbalance = BankTransaction.objects.filter(type = 'credit').aggregate(Sum('amount'))['amount__sum']
        max_value = int(bankbalance/NUMBER_LOAN)
        loans_banktransactions = self.generate_fake_banktransactions(
            NUMBER_LOAN, 
            created_by= adminuser, 
            type='debit',
            amount = factory.Faker('pyint', min_value=100000 , max_value=max_value),
        )
        loans_transactions = self.generate_fake_transactions(loans_banktransactions, created_by=adminuser)
        loans = self.generate_fake_loans(loans_transactions, members, created_by=adminuser)
    
    def generate_fake_banktransactions(self, number, **kwargs):
        transactions = []

        for _ in range(number):
            trans = BankTransactionFactory(**kwargs)
            transactions.append(trans)
        return transactions

    def generate_fake_transactions(self, banktransactions, **kwargs):
        transactions = []
        for t in banktransactions:
            trans = TransactionFactory(
                amount = t.amount,
                type=t.type, 
                description = t.description, 
                status='approved', 
                reference=t,
                created_by=kwargs['created_by']
            )
            t.status = 'assigned'
            t.save()
            transactions.append(trans)

        return transactions

    def generate_fake_shares(self, transactions, members, **kwargs):
        shares = []
        for t in transactions:
            member = random.choice(members)
            share = ShareFactory(
                description='Share, {}:{}'.format(member.get_full_name(),t.description),
                status = 'approved',
                owner = member,
                transaction = t
            )
            shares.append(share)
        return shares

    def generate_fake_savings(self, transactions, members, **kwargs):
        savings = []
        for t in transactions:
            member = random.choice(members)
            share = SavingFactory(
                description='Saving, {}:{}'.format(member.get_full_name(),t.description),
                status = 'approved',
                owner = member,
                transaction = t
            )
            savings.append(share)
        return savings

    def generate_fake_loans(self, transactions, members, **kwargs):
        loans = []
        for t in transactions:

            loantype = 'normal' if t.amount > 500000 else 'emergence'
            duration = random.choice([2, 3, 4, 5, 6, 7, 8, 12,]) if loantype == 'normal' else 1
            member = random.choice(members)
            data = self.get_loan_information(
                t,
                created_by = kwargs['created_by'],
                type=loantype,
                member=member,
                duration = duration,
            )
            loan = LoanFactory(**data)
            loans.append(loan)

        return loans

    def get_loan_information(self, transaction, **kwargs):

            form_fee = 10000 if kwargs['type'] == 'normal' else 0

            #Get Interest
            interest = 1.25 if kwargs['type'] == 'normal' else 1

            #Get LoanFormFee
            loanprocessing = 1 

            #Get LoanInsuranceFee
            insurance = 1

            #Calculate Principle
            principle = ((transaction.amount + form_fee)*100)/98

            #Calculate forminsurance
            insurance_fee = principle * (insurance/100)

            #Calculate loanfee
            loan_fee = principle * (loanprocessing/100)

            #RepaidAmount
            duration = int(kwargs['duration'])
            interest_amount = (principle*(1+ (interest*duration)))/100

            #Monthly installment
            installment_amount = (principle + interest_amount)/duration

            #form fee amount
            return {
                'type':kwargs['type'],
                'principle':principle,
                'duration':duration,
                'interest_rate':interest,
                'status':'issued',
                'member':kwargs['member'],
                'amount_issued':transaction.amount,
                'loan_fee':loan_fee,
                'insurance_fee':insurance_fee,
                'form_fee':form_fee,
                'interest_amount':interest_amount,
                'transaction':transaction,
                'installment_amount':installment_amount,
                'created_by':kwargs['created_by']
            }
            

    def generate_fake_expenses(self, transactions, **kwargs):
        expenses = []
        for t in transactions:
            share = ExpenseFactory(
                description='Expense: {}'.format(t.description),
                status = 'approved',
                transaction = t
            )
            expenses.append(share)
        return expenses
