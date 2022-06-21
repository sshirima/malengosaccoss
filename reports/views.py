from django.views.generic import ListView, View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import RequestConfig
from django.conf import settings


from authentication.permissions import MemberStaffPassTestMixin
from core.views.generic import BaseListView
from reports.tables import ReportMembersTable, ReportTransactionTableFilter, ReportTransactionsTable, LogsTable
from transactions.models import BankTransaction
from reports.selectors import ReportBankTransactionSelector, ReportMemberSelector
from reports.services import LogsfileParser
# Create your views here.

class TransactionReportListView(LoginRequiredMixin,MemberStaffPassTestMixin, ListView):
    template_name ='reports/transactions.html'
    model = BankTransaction
    table_class = ReportTransactionsTable
    filterset_class = ReportTransactionTableFilter

    context_filter_name = 'filter'
    context_table_name = 'table'
    paginate_by = 10

    # Export file
    export_filename = 'file'

    def get_queryset(self, *args, **kwargs):
        qs = ReportBankTransactionSelector.select_transaction_sum_montly()
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        self.queryset = self.filter.qs
        return self.queryset

    def get_context_data(self,*args, **kwargs):
        context = super(TransactionReportListView, self).get_context_data()
        filter = self.filterset_class(self.request.GET, queryset=self.queryset)
        selector = ReportBankTransactionSelector()
        table = self.table_class(selector.transpose_transaction_sum_monthly(self.queryset))
        RequestConfig(self.request, paginate={
                      "per_page": self.get_pagination()}).configure(table)
        context[self.context_filter_name] = filter
        context[self.context_table_name] = table
        return context

    def get_pagination(self):
        pagination = self.request.GET.get('pagination')
        if pagination:
            return int(pagination)
        return self.paginate_by


class ReportMembersListView(LoginRequiredMixin,MemberStaffPassTestMixin, ListView):
    template_name ='reports/transactions.html'
    model = BankTransaction
    table_class = ReportMembersTable
    filterset_class = ReportTransactionTableFilter

    context_filter_name = 'filter'
    context_table_name = 'table'
    paginate_by = 10


    # Export file
    export_filename = 'file'

    def get_queryset(self, *args, **kwargs):
        qs = ReportMemberSelector().get_member_totals()
        # self.filter = self.filterset_class(self.request.GET, queryset=qs)
        self.queryset = qs
        return self.queryset

    def get_context_data(self,*args, **kwargs):
        context = super(ReportMembersListView, self).get_context_data()
        # filter = self.filterset_class(self.request.GET, queryset=self.queryset)
        table = self.table_class(self.queryset)
        RequestConfig(self.request, paginate={
                      "per_page": self.get_pagination()}).configure(table)
        # context[self.context_filter_name] = filter
        context[self.context_table_name] = table
        return context

    def get_pagination(self):
        pagination = self.request.GET.get('pagination')
        if pagination:
            return int(pagination)
        return self.paginate_by

class LogsListView(LoginRequiredMixin,MemberStaffPassTestMixin, ListView):
    template_name ='reports/logs_list.html'
    context_table_name = 'table'
    table_class = LogsTable
    paginate_by = 10
    # Export file
    export_filename = 'logs'

    def get(self, request):
        context = self.get_context_data()

        return render(request, self.template_name, context)

    def get_context_data(self,*args, **kwargs):
        context = {}

        basedir = BASE_DIR = settings.BASE_DIR 
        filepath = basedir / 'logs/application' / 'logs.log'
        reader = LogsfileParser(filepath)

        logs_data = reader.query_log_from_request(self.request)
        table = self.table_class(logs_data)
        RequestConfig(self.request, paginate={"per_page": self.get_pagination()}).configure(table)
        
        context[self.context_table_name] = table
        context['logs_levels']=(('info','Info'), ('warning', 'Warning'), ('error','Error'), )
        return context

    def get_pagination(self):
        pagination = self.request.GET.get('pagination')
        if pagination:
            return int(pagination)
        return self.paginate_by


