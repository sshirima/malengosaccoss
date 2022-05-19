from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class MemberStaffPassTestMixin(UserPassesTestMixin):
    def test_func(self):

        if self.request.user.password_change:
            return not self.request.user.password_change

        return self.request.user.is_staff

    def handle_no_permission(self):

        if self.request.user.password_change:
            return redirect('password-change-required')

        return render(self.request, '403.html')

class MemberNormalPassesTestMixin(UserPassesTestMixin):

    def test_func(self):
        if self.request.user.password_change:
            return not self.request.user.password_change
        return True
            
    def handle_no_permission(self):
        return redirect('password-change-required')