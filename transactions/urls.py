from django.urls import path

from .views import (
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
    path('bank-transaction-multiple-assign', BankTransactionMultipleAssignView.as_view(), name='bank-transaction-multiple-assign'),
]