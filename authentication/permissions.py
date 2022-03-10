from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView
from django_tables2 import RequestConfig


class BaseUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return render(self.request, '403.html')