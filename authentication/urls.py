from django.urls import path

from .views import (
    LogoutView,
    RegistrationView, 
    PasswordChangeChangeView,
    UserProfileUpdateView,
    UserProfileView,
    ActivationView, 
    LoginView, 
    PasswordResetRequestView, 
    PasswordResetChangeView,
    
)


urlpatterns = [
    path('register', RegistrationView.as_view(), name='register'),
    path('activate/<uidb64>/<token>', ActivationView.as_view(), name='activate'),
    path('login', LoginView.as_view(), name='login'),
    path('password-reset-request', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-change/<uidb64>/<token>', PasswordResetChangeView.as_view(), name='password-reset-change'),
    path('password-change', PasswordChangeChangeView.as_view(), name='password-change'),
    path('logout', LogoutView.as_view(), name='logout'),
    #user profile
    path('user-profile', UserProfileView.as_view(), name='user-profile'),
    path('user-profile-update', UserProfileUpdateView.as_view(), name='user-profile-update'),
    #Members information
]