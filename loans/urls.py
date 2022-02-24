from django.urls import path

from loans.views import (
    LoanListView,
    LoanCreateFromBankTransactionView,
    LoanDetailView
)

urlpatterns = [
    path('loans-list', LoanListView.as_view(), name='loans-list'),
    path('loan-detail/<id>', LoanDetailView.as_view(), name='loan-detail'),
    path('loan-create/<uuid>', LoanCreateFromBankTransactionView.as_view(), name='loan-create'),
]