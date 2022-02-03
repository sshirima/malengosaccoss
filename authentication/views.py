
from django.shortcuts import redirect, render
from django.urls import reverse
from django.urls.base import  reverse_lazy
from django.views.generic import CreateView, View
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.forms import PasswordChangeForm
from django_tables2 import RequestConfig
from django.db.models import Sum
from django.views.generic import CreateView, ListView, DetailView

from authentication.models import User
from authentication.tables import MemberTable, MemberTableFilter

from .forms import PasswordResetChangeForm, RegistrationForm, LoginForm, PasswordResetRequestForm, UserProfileUpdateForm
from .services import PasswordResetService, RegistrationService, LoginService, UserProfileService

from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class RegistrationView(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'authentication/register.html'

    def post(self, request):
        form = RegistrationForm(request.POST)
        context = {}
        registrationService = RegistrationService(request)

        if not form.is_valid():
            context = self.get_context_data_post(request, form)
            return render(request, self.template_name, context) 

        created, user = registrationService.create_user(form.cleaned_data)

        
        if not created and user is None:
            context = self.get_context_data_post(request, form)
            return render(request, self.template_name, context) 

        messages.success(request, 'Account created successful, an activation email will be sent by the administrator')
        return redirect('login')
        

    def get_context_data_post(self, request, form):
        context = {}
        context['values'] = request.POST
        context['form'] = form
        return context
                


class ActivationView(View):

    def get(self, request, uidb64, token):

        registrationService = RegistrationService(request)

        message, activated, user = registrationService.activate_user(uidb64, token)

        if activated and user is not None:
            messages.success(request, 'Account activated successfully')

        else:
            messages.error(request, 'There was an error activating your account')

        return redirect('login')

class LoginView(View):

    template_name = 'authentication/login.html'

    def get(self, request):
        return render(request, self.template_name, {'form': LoginForm})

    def post(self, request):
        form = LoginForm(request.POST)
        context = {}
        loginservice = LoginService(request)

        if form.is_valid():
            message, authenticated, user = loginservice.authenticate_user(form.cleaned_data)

            if authenticated and user is not None:
                return redirect('dashboard')
            
            messages.error(request, 'Fails to authenticate username/password')
        else:
            messages.error(request, 'Fill all required fields')

        context['form'] = form
        return render(request, self.template_name, context)


class LogoutView(View):

    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

class PasswordResetRequestView(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):

        form = PasswordResetRequestForm(request.POST)
        context = {}
        resetService = PasswordResetService(request)

        if form.is_valid():

            user, password_reset_url = resetService.create_password_reset_url(form.cleaned_data)

            if user is not None:
                email_sent = resetService.send_password_reset_email(user, password_reset_url)

                if email_sent:
                    messages.success(request, 'Password reset link has been sent')
                    return render(request, 'authentication/reset_password_complete.html')

                messages.error(request, 'Fails to send password activation link, please try again')

            messages.error(request, 'Account does not exist')
            

        else:
            messages.error(request, 'Error on the input fields')

        return render(request, 'authentication/reset_password.html')
        

class PasswordResetChangeView(View):

    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token,
        }
        resetService = PasswordResetService(request)

        token_valid = resetService.check_token_validity(uidb64, token)

        if not token_valid:
            messages.error(request, "Password link is invalid, please request a new one")

            return render(request, 'authentication/reset_password.html')

        return render(request, 'authentication/set_newpassword.html', context)

    def post(self, request, uidb64, token):

        form = PasswordResetChangeForm(request.POST)
        resetService = PasswordResetService(request)
        context = {
            'uidb64':uidb64,
            'token':token,
        }

        if form.is_valid():
            reset_password = resetService.reset_password(uidb64, form.cleaned_data)

            if reset_password:
                messages.success(request, 'Password reset successful')
                return redirect('login')

            messages.error(request, 'Error occurs during password reset')

        else:
            messages.error(request, 'Invalid input fields')

        return render(request, 'authentication/set_newpassword.html', context) 


class LogoutView(LoginRequiredMixin,View):

    def get(self, request):
        auth.logout(request)
        messages.info(request, 'You have been logged out')
        return redirect('login')

#Require login Mixin    
class PasswordChangeChangeView(LoginRequiredMixin, View):

    template_name = 'authentication/change_password.html'

    def get(self, request):
        return render(request, self.template_name, {'form': PasswordChangeForm})

    def post(self, request):

        form = PasswordChangeForm(request.user, request.POST)

        resetService = PasswordResetService(request)

        if form.is_valid():
            request,form, changed = resetService.change_password(request, form)

            if changed:
                messages.success(request, 'Password updated successfull')

                return redirect('user-profile')
            else:
                messages.error(request, 'Error updating your password')


        return render(request, self.template_name, {'form': form})


class UserProfileView(LoginRequiredMixin,  View):

    template_name = 'authentication/user_profile.html'

    def get(self, request):
        return render(request, self.template_name)


class UserProfileUpdateView(LoginRequiredMixin, View):

    template_name = 'authentication/user_profile_update.html'

    def get(self, request):

        return render(request, self.template_name)

    def post(self, request):
        form = UserProfileUpdateForm(request.POST)
        
        if form.is_valid():
            service = UserProfileService(request)
            code, updated, user = service.update_user_profile(form.cleaned_data, request.user)

            if updated and user is not None:
                messages.success(request, 'User profile updated successful!')
                return redirect('user-profile')

            messages.error(request, 'Fails to update user profile')

        return render(request, self.template_name, {'form': form})


class MemberListView(LoginRequiredMixin, ListView):
    template_name ='authentication/member_list.html'
    model = User
    
    table_class = MemberTable
    table_data = User.objects.all()
    filterset_class = MemberTableFilter
    context_filter_name = 'filter'

    def get_context_data(self,*args, **kwargs):
        context = super(MemberListView, self).get_context_data()
        queryset = self.get_queryset(**kwargs)
        filter = MemberTableFilter(self.request.GET, queryset=queryset)
        table = MemberTable(filter.qs)
        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['filter']=filter
        context['table']=table
        context['total_members'] = queryset.count()

        return context

class MemberDetailView(LoginRequiredMixin, DetailView):
    template_name = 'authentication/member_detail.html'
    model = User
    context_object_name = 'member'
    slug_field = 'id'
    slug_url_kwarg = 'id'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.filter(id=self.kwargs['id'])
        else:
            return User.objects.none()


class MemberSendActivationLinkView(View):

    def get(self, request, id):
        user = User.objects.get(id=id)

        if not request.user.is_staff:
            messages.error(request, 'You dont have permission to perform this operation')
            return redirect('members-list')

        if not user:
            messages.error(request, 'User does not exist')
            return redirect('members-list')

        if user.is_active:
            messages.error(request, 'User already activated')
            return redirect(reverse('member-detail', user.id))

        registrationService = RegistrationService(request)

        activation_url = registrationService.create_activation_url(user)

        activation_link_sent = registrationService.send_activation_email(user, activation_url)
        
        if not activation_link_sent:
            messages.error(request, 'Fails to send activation link, Please try agail later')
            return redirect(reverse('member-detail', user.id))

        messages.success(request, 'Account activation has been sent to: {}'.format(user.email))
        return redirect(reverse('member-detail', args=[user.id]))


class MemberSendPasswordResetLinkView(View):

    def get(self, request, id):

        if not request.user.is_staff:
            messages.error(request, 'You dont have permission to perform this operation')
            return redirect('members-list')

        user = User.objects.get(id=id)

        if user is None:
            messages.error(request, 'Account does not exist')
            return redirect('members-list')

        resetService = PasswordResetService(request)

        user, password_reset_url = resetService.create_password_reset_url_user(user)

        if not user.is_active:
            messages.error(request, 'User is disabled, please activate user first')
            return redirect(reverse('member-detail', args=[user.id]))

        email_sent = resetService.send_password_reset_email(user, password_reset_url)

        if not email_sent:
            messages.error(request, 'Fails to send password activation link, please try again')
        
        messages.success(request, 'Password reset link has been sent')
        return redirect(reverse('member-detail', args=[user.id]))

        

        

        # registrationService = RegistrationService(request)

        # activation_url = registrationService.create_activation_url(user)

        # activation_link_sent = registrationService.send_activation_email(user, activation_url)
        
        # if not activation_link_sent:
        #     messages.error(request, 'Fails to send activation link, Please try agail later')
        #     return redirect(reverse('member-detail', user.id))

        # messages.success(request, 'Account activation has been sent to: {}'.format(user.email))
        # return redirect(reverse('member-detail', args=[user.id]))

        