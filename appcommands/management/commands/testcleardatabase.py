
from django.db import transaction
from django.core.management.base import BaseCommand

from authentication.models import User
from members.models import Member
from transactions.models import BankTransaction, Transaction
from shares.models import Share
from savings.models import Saving
from loans.models import Loan, LoanRepayment
from expenses.models import Expense

class Command(BaseCommand):
    help = "Clearing all data on the database ..."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing database ....')
        models = [Share, Saving, LoanRepayment, Loan, Expense, Transaction, BankTransaction, Member]

        for m in models:
            m.objects.all().delete()

        for user in User.objects.all():
            if user.email == 'admin@localhost.com':
                continue
            user.delete()

        self.stdout.write('Database cleared successfull ....')