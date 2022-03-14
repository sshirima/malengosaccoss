from django.shortcuts import render

from django.shortcuts import redirect, render
from django.urls import reverse
from django.urls.base import  reverse_lazy
from django.views.generic import CreateView, View
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.forms import PasswordChangeForm
from authentication.models import User
from core.views.generic import BaseListView
from django_tables2 import RequestConfig
from django.db.models import Sum
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
from authentication.services import RegistrationService, PasswordResetService
from loans.models import Loan, LoanRepayment
from loans.tables import LoanTable, LoanTableFilter
from shares.models import Share
from savings.models import Saving
from savings.tables import SavingTable, SavingTableFilter
from loans.tables import LoanRepaymentTable, LoanRepaymentTableFilter
from .models import Member, GENDER_STATUS
from .tables import MemberTable, MemberTableExport, MemberTableFilter
from shares.tables import ShareTable, ShareTableFilter
from authentication.permissions import BaseUserPassesTestMixin

class MemberListView(LoginRequiredMixin,BaseUserPassesTestMixin, BaseListView):
    template_name ='members/member_list.html'
    model = Member
    table_class = MemberTable
    filterset_class = MemberTableFilter
    context_filter_name = 'filter'
    context_table_name = 'table'
    paginate_by = 10

    table_class_export = MemberTableExport
    export_filename = 'Members'

    def get_queryset(self, *args, **kwargs):
        filters = {}
        return super(MemberListView, self).get_queryset(**filters)

    def get_context_data(self,*args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        context = super(MemberListView, self).get_context_data(queryset)
        context['genders']= GENDER_STATUS
        context['member_status'] = (('active', 'Active'),('inactive', 'Inactive'))
        return context

class MemberDetailView(LoginRequiredMixin,BaseUserPassesTestMixin, DetailView):
    template_name = 'members/member_detail.html'
    model = Member
    context_object_name = 'member'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        
        return Member.objects.select_related('user').filter(id=self.kwargs['id'])

    def get_context_data(self,*args, **kwargs):
        context = super(MemberDetailView, self).get_context_data()
        context = self.get_member_shares_table(self.object, context)
        context = self.get_member_loans_table(self.object, context)
        context = self.get_member_savings_table(self.object, context)
        context = self.get_member_loanrepayment_table(self.object, context)
        return context

    def get_member_shares_table(self, member, context):

        queryset = Share.objects.filter(owner=member)
        filter = ShareTableFilter(self.request.GET, queryset=queryset)
        table = ShareTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)

        if not queryset:
            context['total_shares'] = 0
        else:
            context['total_shares'] = queryset.aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        context['shares_filter']=filter
        context['shares_table']=table

        return context

    def get_member_loans_table(self, member, context):

        queryset = Loan.objects.filter(member=member)
        filter = LoanTableFilter(self.request.GET, queryset=queryset)
        table = LoanTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        if not queryset:
            context['total_loan'] = 0
        else:
            aggregate_sum = queryset.aggregate(Sum('principle'), Sum('interest_amount'))
            context['total_loan'] = aggregate_sum['principle__sum'] + aggregate_sum['interest_amount__sum']
        context['loan_filter']=filter
        context['loan_table']=table

        return context

    def get_member_loanrepayment_table(self, member, context):

        queryset = LoanRepayment.objects.filter(loan__member=member)
        filter = LoanRepaymentTableFilter(self.request.GET, queryset=queryset)
        table = LoanRepaymentTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        if not queryset:
            context['total_loanrepayments'] = 0
        else:
            aggregate_sum = queryset.aggregate(Sum('transaction__amount'))
            context['total_loanrepayments'] = aggregate_sum['transaction__amount__sum']
        context['loanrepayment_filter']=filter
        context['loanrepayment_table']=table

        return context

    def get_member_savings_table(self, member, context):

        queryset = Saving.objects.filter(owner=member)
        filter = SavingTableFilter(self.request.GET, queryset=queryset)
        table = SavingTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        if not queryset:
            context['total_saving'] = 0
        else:
            context['total_saving'] = queryset.aggregate(Sum('transaction__amount'))['transaction__amount__sum']
        context['saving_filter']=filter
        context['saving_table']= table

        return context

class MemberSendActivationLinkView(LoginRequiredMixin,BaseUserPassesTestMixin,View):

    def get(self, request, id):

        member = Member.objects.get(id=id)
        user = member.user

        if not request.user.is_staff:
            messages.error(request, 'You dont have permission to perform this operation')
            return redirect('members-list')

        if not user:
            messages.error(request, 'User does not exist')
            return redirect('members-list')

        if user.is_active:
            messages.error(request, 'User already activated')
            return redirect(reverse('member-detail', member.id))

        registrationService = RegistrationService(request)

        activation_url = registrationService.create_activation_url(user)

        activation_link_sent = registrationService.send_activation_email(user, activation_url)
        
        if not activation_link_sent:
            messages.error(request, 'Fails to send activation link, Please try agail later')
            return redirect(reverse('member-detail', member.id))

        messages.success(request, 'Account activation has been sent to: {}'.format(user.email))
        return redirect(reverse('member-detail', args=[member.id]))

class MemberSendPasswordResetLinkView(LoginRequiredMixin,BaseUserPassesTestMixin,View):

    def get(self, request, id):

        if not request.user.is_staff:
            messages.error(request, 'You dont have permission to perform this operation')
            return redirect('members-list')

        member = Member.objects.get(id=id)
        user = member.user

        if user is None:
            messages.error(request, 'Account does not exist')
            return redirect('members-list')

        resetService = PasswordResetService(request)

        user, password_reset_url = resetService.create_password_reset_url_user(user)

        if not user.is_active:
            messages.error(request, 'User is disabled, please activate user first')
            return redirect(reverse('member-detail', args=[member.id]))

        email_sent = resetService.send_password_reset_email(user, password_reset_url)

        if not email_sent:
            messages.error(request, 'Fails to send password activation link, please try again')
            return redirect(reverse('member-detail', args=[member.id]))
        
        messages.success(request, 'Password reset link has been sent')
        return redirect(reverse('member-detail', args=[member.id]))
