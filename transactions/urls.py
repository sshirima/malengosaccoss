from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (
    BankStatementDeleteView,
    BankStatementDetailView,
    BankStatementListView,
    TransactionCreateView,
    TransactionUpdateView, 
    TransactionDetailView, 
    TransactionListView,
    TransactionDeleteView,
    BankTransactionImportView,
    BankTransactionListView,
    BankTransactionAssignView,
    BankTransactionDetailView,
    BankTransactionMultipleAssignView,
    BankTransactionMultipleAssignConfirmView,
    get_member_loans
)

urlpatterns = [
    path('list', TransactionListView.as_view(), name='transactions-list'),
    path('create', TransactionCreateView.as_view(), name='transaction-create'),
    path('detail/<id>', TransactionDetailView.as_view(), name='transaction-detail'),
    path('update/<id>', TransactionUpdateView.as_view(), name='transaction-update'),
    path('delete/<id>', TransactionDeleteView.as_view(), name='transaction-delete'),
    path('bank-transaction-list', BankTransactionListView.as_view(), name='bank-transaction-list'),
    path('bank-transaction-import', BankTransactionImportView.as_view(), name='bank-transaction-import'),
    path('bank-transaction-detail/<id>', BankTransactionDetailView.as_view(), name='bank-transaction-detail'),
    path('bank-transaction-assign/<uuid>', BankTransactionAssignView.as_view(), name='bank-transaction-assign'),
    path('multiple-assign', BankTransactionMultipleAssignView.as_view(), name='bank-transaction-multiple-assign'),
    path('multiple-assign-confirm', BankTransactionMultipleAssignConfirmView.as_view(), name='multiple-assign-confirm'),
    path('get-member-loans', csrf_exempt(get_member_loans)),
    #Bank statement URLS
    path('bank-statement-list', BankStatementListView.as_view(), name='bank-statement-list'),
    path('bank-statement-detail/<id>', BankStatementDetailView.as_view(), name='bank-statement-detail'),
    path('bank-statement-delete/<id>', BankStatementDeleteView.as_view(), name='bank-statement-delete'),
]