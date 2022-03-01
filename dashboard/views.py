import imp
from django.shortcuts import render
from django.views.generic import View

from shares.models import Share
from transactions.models import Transaction, BankTransaction
from members.models import Member
from savings.models import Saving
from expenses.models import Expense
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Sum
# Create your views here.


class DashboardView(LoginRequiredMixin, View):
    template_name = 'dashboard/index.html'

    def get(self, request):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def get_context_data(self, request):
        context = {}
        #Total Share amount
        context['share_amount_sum'] = Share.objects.all().aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        #Total Saving amount
        context['saving_amount_sum']  = Saving.objects.all().aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        #Total Expenses
        context['expense_amount_sum']  = Expense.objects.all().aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        
        #Total members
        context['member_all_count'] = Member.objects.all().count()
        #Loan balance

        #Total Pending Loans

        return context