from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from dashboard.views import (
    DashboardView,
    get_shares,
    get_savings
)


urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('get-shares', csrf_exempt(get_shares)),
    path('get-savings', csrf_exempt(get_savings)),
]