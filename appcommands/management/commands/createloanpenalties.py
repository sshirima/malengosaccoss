from django.core.management.base import BaseCommand
from django.db.models import Sum
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from loans.models import Loan, LoanRepayment

class Command(BaseCommand):
    help = 'Creating Loans Penalties'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating loan penalties for loans ....')

        loans = Loan.objects.select_related('transaction__reference').filter(repayment_status__in = ['issued','repayment', 'default'])
        for loan in loans:
            #Get number of days from date created
            statement = {}
            today = datetime.now()
            created_date = loan.transaction.reference.date_trans

            first_paying_date = self.get_next_payment_date(created_date)

            principle_repayment = loan.principle/loan.duration

            r = relativedelta(today, created_date)
            months_from_paid = (r.years * 12) + r.months

            interest_amount = self.calculate_interest_amount(loan.principle, loan.interest_rate, months_from_paid)
            statement['principle'] = loan.principle
            statement['t']=months_from_paid
            statement['interest'] = int(interest_amount)
            print(statement)

            # loanrepayments = LoanRepayment.objects.filter(loan = loan).annotate(sum=Sum('transaction__reference__amount'))
            # print(loanrepayments)

    def calculate_interest_amount(self, p, r, t):
        return (p*(1+ (r*t)))/100

    def get_next_payment_date(self, date):

        next_paying_date = date + timedelta(days=31) + relativedelta(months=1)

        return next_paying_date.replace(day=5)