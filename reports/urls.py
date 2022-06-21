from django.urls import path

from reports.views import (
    TransactionReportListView,
    ReportMembersListView,
    LogsListView
)

urlpatterns = [
    path('transactions', TransactionReportListView.as_view(), name='report-transactions'),
    path('members', ReportMembersListView.as_view(), name='report-members'),
    path('logs-list', LogsListView.as_view(), name='logs-list')
]