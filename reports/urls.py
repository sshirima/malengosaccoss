from django.urls import path

from reports.views import (
    TransactionReportListView,
    ReportMembersListView
)

urlpatterns = [
    path('transactions', TransactionReportListView.as_view(), name='report-transactions'),
    path('members', ReportMembersListView.as_view(), name='report-members')
]