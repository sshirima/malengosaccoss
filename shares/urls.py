from django.urls import path

from shares.views import (
    # ShareCreateView,
    ShareUpdateView, 
    ShareDetailView, 
    ShareListView,
    ShareDeleteView,
    ShareAuthorizeView,
)

urlpatterns = [
    path('list', ShareListView.as_view(), name='shares-list'),
    # path('create/<uuid>', ShareCreateView.as_view(), name='share-create'),
    path('detail/<id>', ShareDetailView.as_view(), name='share-detail'),
    path('update/<id>', ShareUpdateView.as_view(), name='share-update'),
    path('delete/<id>', ShareDeleteView.as_view(), name='share-delete'),
    path('authorize/<uuid>', ShareAuthorizeView.as_view(), name='share-authorize'),
]