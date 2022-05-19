from django.urls import path

from savings.views import (
    SavingUpdateView, 
    SavingDetailView, 
    SavingListView,
    SavingDeleteView,
    # SavingCreateView,
)

urlpatterns = [
    path('savings-list', SavingListView.as_view(), name='savings-list'),
    path('saving-detail/<id>', SavingDetailView.as_view(), name='saving-detail'),
    path('saving-update/<id>', SavingUpdateView.as_view(), name='saving-update'),
    path('saving-delete/<id>', SavingDeleteView.as_view(), name='saving-delete'),
    # path('saving-create/<uuid>', SavingCreateView.as_view(), name='saving-create'),
]