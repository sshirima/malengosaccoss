from django.urls import path

from members.views import (
    MemberListView,
    MemberDetailView,
    MemberSendActivationLinkView,
    MemberSendPasswordResetLinkView,
)

urlpatterns = [
    path('members', MemberListView.as_view(), name='members-list'),
    path('member-detail/<id>', MemberDetailView.as_view(), name='member-detail'),
    path('member-send-activation-link/<id>', MemberSendActivationLinkView.as_view(), name='member-send-activation-link'),
    path('member-send-password-reset-link/<id>', MemberSendPasswordResetLinkView.as_view(), name='member-send-password-reset-link'),
]