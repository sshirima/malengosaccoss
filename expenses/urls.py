from django.urls import path

from expenses.views import (
    ExpenseUpdateView, 
    ExpenseDetailView, 
    ExpenseListView,
    ExpenseDeleteView,
    ExpenseCreateView,
)

urlpatterns = [
    path('expenses-list', ExpenseListView.as_view(), name='expenses-list'),
    path('expense-detail/<id>', ExpenseDetailView.as_view(), name='expense-detail'),
    path('expense-update/<id>', ExpenseUpdateView.as_view(), name='expense-update'),
    path('expense-delete/<id>', ExpenseDeleteView.as_view(), name='expense-delete'),
    path('expense-create/<uuid>', ExpenseCreateView.as_view(), name='expense-create'),
]