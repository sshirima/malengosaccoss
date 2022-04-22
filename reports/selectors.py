from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.db.models import F

from transactions.models import BankTransaction
from savings.models import Saving
from shares.models import Share
from loans.models import Loan


class ReportBankTransactionSelector():

    def select_transaction_sum_montly():
        return BankTransaction.objects.annotate(month=TruncMonth('date_trans')).values(
            'month').annotate(sum=Sum('amount')) .order_by( '-month').values('month', 'sum', 'type')
        
    def transpose_transaction_sum_monthly(self, transactions):
        results = []
        #Transpose the list
        for t in transactions:
            flag = False
            for r in results:
                if r['month'] == t['month']:
                    r['total_'+t['type']] = t['sum']
                    flag = True
                    break
                continue
            if not flag:
                results.append({'month':t['month'], 'total_'+t['type']:t['sum']})
        return results


class ReportMemberSelector():

    def get_member_totals(self):
        shares = self.get_members_totals(Share, id='owner__id',member='owner',first_name='owner__first_name', middle_name='owner__middle_name', last_name= 'owner__last_name', email='owner__user__email')
        savings = self.get_members_totals(Saving,id='owner__id', member='owner',first_name='owner__first_name', middle_name='owner__middle_name', last_name= 'owner__last_name', email='owner__user__email')
        loans = self.get_members_totals(Loan, id='member__id', member='member',first_name='member__first_name', middle_name='member__middle_name', last_name= 'member__last_name', email='member__user__email')

        #Formating data for presentation
        results = []
        results = self.get_formated_data(shares, results, 'share')
        results = self.get_formated_data(savings, results, 'saving')
        results = self.get_formated_data(loans, results, 'loan')

        return results

    def get_formated_data(self, object_list, results, scope):

        for s in object_list.iterator():
            row = next((sub for sub in results if sub['email'] == s['email']), None)
            if row:
                row[scope+'_total'] = s['sum']
                continue
            results.append(
                {
                    'id':s['id'],
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
            kwargs['first_name']),id=F(kwargs['id']), email=F(kwargs['email']), middle_name=F(kwargs['middle_name']), last_name=F(kwargs['last_name'])).values('id','email','first_name', 'middle_name', 'last_name', 'sum')
