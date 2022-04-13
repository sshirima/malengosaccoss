from operator import attrgetter
from unittest import result
from django.core.management.base import BaseCommand
from django.db.models import F
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from itertools import chain

from members.models import Member
from authentication.models import User
from savings.models import Saving
from shares.models import Share
from transactions.models import BankTransaction
from loans.models import Loan


class Command(BaseCommand):

    def handle(self,  *args, **kwargs):

        shares = self.get_members_totals(Share, member='owner',first_name='owner__first_name', middle_name='owner__middle_name', last_name= 'owner__last_name', email='owner__user__email')
        savings = self.get_members_totals(Saving, member='owner',first_name='owner__first_name', middle_name='owner__middle_name', last_name= 'owner__last_name', email='owner__user__email')
        loans = self.get_members_totals(Loan, member='member',first_name='member__first_name', middle_name='member__middle_name', last_name= 'member__last_name', email='member__user__email')

        
        # results = self.get_formated_data(shares, results, 'share')
        # results = self.get_formated_data(savings, results, 'saving')
        # results = self.get_formated_data(loans, results, 'loan')

        
        # report = chain(shares, savings)

        # print(report)

    def get_formated_data(self, object_list, results, scope):

        for s in object_list.iterator():
            row = next((sub for sub in results if sub['email'] == s['email']), None)
            if row:
                row[scope+'_total'] = s['sum']
                continue
            results.append(
                {
                    'email':s['email'],
                    'first_name':s['first_name'],
                    'middle_name':s['middle_name'],
                    'last_name':s['last_name'],
                    scope+'_total':s['sum'],
                }
            )

        for r in results:
            if not scope+'_total' in r.keys():
                r[scope+'_total'] = 0

        return results

    def get_members_totals(self, object, **kwargs):
        return object.objects.select_related('member', 'user').values(kwargs['member']).annotate(sum=Sum('transaction__reference__amount'), first_name=F(
            kwargs['first_name']), email=F(kwargs['email']), middle_name=F(kwargs['middle_name']), last_name=F(kwargs['last_name'])).values('email','first_name', 'middle_name', 'last_name', 'sum')

        
    def get_monthly_transactions(self):
        self.stdout.write('Creating reports ....')
        transactions = BankTransaction.objects.annotate(month=TruncMonth('date_trans')).values(
            'month').annotate(sum=Sum('amount')) .order_by('-month').values('month', 'sum', 'type')
        # shares = Share.objects.values(month = F('transaction__reference__date_trans__month')).annotate(sum=Sum('transaction__amount'))
        results = []
        for t in transactions:
            flag = False
            for r in results:
                if r['month'] == t['month']:
                    r['total_'+t['type']] = t['sum']
                    flag = True
                    break
                continue
            if not flag:
                results.append(
                    {'month': t['month'], 'total_'+t['type']: t['sum']})
        return results
