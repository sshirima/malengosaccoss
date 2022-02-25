from django.urls import path

from loans.views import (
    LoanListView,
    LoanCreateFromBankTransactionView,
    LoanDetailView,
    LoanRepaymentCreateView,
    LoanRepaymentDetailView,
    LoanRepaymentMemberSelectView,
    LoanRepaymentListView,
)

urlpatterns = [
    path('loans-list', LoanListView.as_view(), name='loans-list'),
    path('loan-detail/<id>', LoanDetailView.as_view(), name='loan-detail'),
    path('loan-create/<uuid>', LoanCreateFromBankTransactionView.as_view(), name='loan-create'),
    path('loanrepayment-list', LoanRepaymentListView.as_view(), name='loanrepayment-list'),
    path('loanrepayment-detail/<id>', LoanRepaymentDetailView.as_view(), name='loanrepayment-detail'),
    path('loanrepayment-create/<uuid1>/<uuid2>', LoanRepaymentCreateView.as_view(), name='loanrepayment-create'),
    path('loanrepayment-select-member/<uuid>', LoanRepaymentMemberSelectView.as_view(), name='loanrepayment-select-member'),
]