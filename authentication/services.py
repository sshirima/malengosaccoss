
import email
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import update_session_auth_hash
from django.conf import settings # import the settings file

from members.models import Member
from .models import User, UserManager
from .emails import ActivationEmailSender
from .utils import token_generator

class RegistrationService():

    def __init__(self, request):
        self.request = request

    def create_user(self, data):
        
        try:
            user = User.objects.create(
                email=UserManager.normalize_email(data['email']),
            )
            user.set_password(data['password1'])
            user.is_active = False
            user.save()

            #Create member
            member = Member.objects.create(
                first_name = data['first_name'],
                middle_name = data['middle_name'],
                last_name = data['last_name'],
                mobile_number = data['mobile_number'],
                gender = data['gender'],
                user = user,
            )

            return (True, user)
        except Exception as e:
            print('ERROR, creating new user account: {}'.format(str(e)))
            return None
        


    def create_activation_url(self, user):
        try:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(self.request).domain
            token = token_generator.make_token(user)

            activation_link = reverse('activate', kwargs={
                        'uidb64':uidb64,
                        'token':token,
                    })

            return 'http://{}{}'.format(domain,activation_link)

        except Exception as e:
            print('ERROR, creating activation link url: {}'.format(str(e)))
            return None


    def send_activation_email(self, user, activation_url):
        try:
            mail_sender = ActivationEmailSender(self.request)
            email_body = email_body = 'Hi, Please use below link to activate your account\n'+activation_url
            email_subject = 'Account activation email'
            sender = settings.EMAIL_HOST_USER
            receivers = [user.email]
            return mail_sender.send(subject=email_subject, body=email_body, from_email=sender, to=receivers)
            
        except Exception as e:
            print('ERROR, preparing activation email: {}'.format(str(e)))
            return False

    def activate_user(self, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                
                return ('Token already used',False, None)

            if user.is_active:
                return ('User is already activated',False, None)

            user.is_active = True
            user.save()
            #Activate member
            member = user.member
            member.is_active = True
            member.save()
            
            return ('User activated', True, user)

        except Exception as e:
            print('ERROR, activating user: {}'.format(str(e)))
            return ('Fails to activate user', False, None)

class LoginService():

    def __init__(self, request):
        self.request = request

    def authenticate_user(self, credentials):
        email = credentials['email']
        password = credentials['password']

        user = auth.authenticate(username=email, password=password)
        
        if user is not None:

            if user.is_active:
                auth.login(self.request, user)
                return ('', True, user)
            else:
                print('ERROR, Account not activated')
                return ('',False, None )
        else:
            print('ERROR, Fail to authenticate')
            return ('', False, None)

class PasswordResetService():

    def __init__(self, request):
        self.request = request


    def create_password_reset_url(self, data):
        try:
            user = User.objects.filter(email=data['email']).first()

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(self.request).domain
            token = PasswordResetTokenGenerator().make_token(user)
            password_reset_url = reverse('password-reset-change', kwargs={
                'uidb64':uidb64,
                'token':token,
            })
            return (user, 'http://{}{}'.format(domain,password_reset_url))
        
        except Exception as e:
            print('ERROR, creating password reset link: {}'.format(str(e)))
            return (None, '')


    def create_password_reset_url_user(self, user):
        try:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(self.request).domain
            token = PasswordResetTokenGenerator().make_token(user)
            password_reset_url = reverse('password-reset-change', kwargs={
                'uidb64':uidb64,
                'token':token,
            })
            return (user, 'http://{}{}'.format(domain,password_reset_url))
        
        except Exception as e:
            print('ERROR, creating password reset link: {}'.format(str(e)))
            return (None, '')


    def send_password_reset_email(self, user, reset_url):
        try:
            mail_sender = ActivationEmailSender(self.request)
            email_body = 'Hi there,  Please use below link to reset your password\n'+reset_url
            email_subject = 'Password reset instruction'
            sender = settings.EMAIL_HOST_USER
            receivers = [user.email]
            return mail_sender.send(subject=email_subject, body=email_body, from_email=sender, to=receivers)
            
        except Exception as e:
            print('ERROR, sending password reset email: {}'.format(str(e)))
            return False


    def check_token_validity(self, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if PasswordResetTokenGenerator().check_token(user, token):
                
                return True

        except Exception as e:
            print('ERROR, checking password reset token validity: {}'.format(str(e)))
            return False

        return False

    def reset_password(self, uidb64, data):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            user.set_password(data['password1'])
            user.save()

            return True

        except Exception as e:
            print('ERROR, reseting password: {}'.format(str(e)))
            return False

    def change_password(self,request, form):

        try:
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return (request, form,True)
        except Exception as e:
            print('ERROR, changing password: {}'.format(str(e)))
            return (form, request, False)


class UserProfileService():

    
    def __init__(self, request):
        self.request  = request


    def update_user_profile(self, data, user):

        try:
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.mobile_number = data['mobile_number']
            user.save()

            return ('', True, user)

        except Exception as e:
            print('ERROR, updating user profile: {}'.format(str(e)))
            return ('', False, None)
