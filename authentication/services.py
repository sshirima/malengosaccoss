
import email
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import update_session_auth_hash
from django.conf import settings # import the settings file
import logging

from members.models import Member
from .models import User, UserManager
from .emails import ActivationEmailSender
from .utils import token_generator
from core.utils import log_error

logger = logging.getLogger(__name__)

class RegistrationService():

    def __init__(self, request=None):
        self.request = request

    def create_user(self, **data):
        
        try:
            is_active = data.pop('is_active', False)
            password_change = data.pop('password_change', False)
            
            #Check if email exist
            if User.objects.filter(email=data['email']).exists():
                print('User exits: {}'.format(data['email']))
                return False, None

            user = User.objects.create(
                email=UserManager.normalize_email(data['email']),
            )

            user.set_password(data['password1'])
            user.password_change = password_change
            user.is_active = is_active
            user.save()

            #Create member
            Member.objects.create(
                first_name = data['first_name'],
                middle_name = data['middle_name'],
                last_name = data['last_name'],
                mobile_number = data['mobile_number'],
                gender = data['gender'],
                user = user,
            )
            logger.info('Success, member registered: {}'.format(user.email))
            return (True, user)

        except Exception as e:

            if 'user' in locals():
                if user:
                    user.delete()

            log_error("Error, creating user", e)
            return False, None
        


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
            log_error("Error, creating activation url", e)
            return None


    def send_activation_email(self, user, activation_url):
        try:
            mail_sender = ActivationEmailSender(self.request)
            email_body = email_body = 'Hi, Please use below link to activate your account\n'+activation_url
            email_subject = 'Account activation email'
            sender = settings.EMAIL_HOST_USER
            receivers = [user.email]
            sent = mail_sender.send(subject=email_subject, body=email_body, from_email=sender, to=receivers)
            return sent
            
        except Exception as e:
            log_error("Error, sending activation email", e)
            return False

    def activate_user(self, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                logger.warning('Token already used or expired: {}'.format(user.email))
                return ('Token already used or expired',False, None)

            if user.is_active:
                logger.warning('The user is already activated: {}'.format(user.email))
                return ('The user is already activated',False, None)

            user.is_active = True
            user.save()
            #Activate member
            member = user.member
            member.is_active = True
            member.save()
            logger.info('User activation succsess: {}'.format(user.email))
            return ('', True, user)

        except Exception as e:
            log_error("Error activating user", e)
            return ('Error activating user', False, None)

class LoginService():

    def __init__(self, request):
        self.request = request

    def authenticate_user(self, credentials):
        try:
            email = credentials['email']
            password = credentials['password']

            user = auth.authenticate(username=email, password=password)
            
            if user is not None:
                auth.login(self.request, user)
                logger.info('Success, user logged in: {}'.format(email))
                return ('', True, user)
                
            logger.warning('Fails to authenticate user: {}'.format(email))
            return ('Fails to authenticate user', False, None)

        except Exception as e:
            log_error("Error authenticating user", e)
            return ('Error authenticating user', False, None)

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
            log_error("Error creating password reset url", e)
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
            log_error("Error creating password reset url for user", e)
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
            log_error("Error sending password reset email", e)
            return False


    def check_token_validity(self, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if PasswordResetTokenGenerator().check_token(user, token):
                return True

        except Exception as e:
            log_error("Error checking token validity", e)
            return False

        return False

    def reset_password(self, uidb64, data):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            user.set_password(data['password1'])
            user.save()

            logger.info('Success reseting password: {}'.format(user.email))
            return True

        except Exception as e:
            log_error("Error, reseting password", e)
            return False

    def change_password(self,request, form):

        try:
            user = form.save()

            if user.password_change:
                user.password_change = False
                user.save()

            update_session_auth_hash(request, user)  # Important!
            logger.info('Success changing password: {}'.format(user.email))
            return (request, form,True)
            
        except Exception as e:
            log_error("Error, changing password", e)
            return (form, request, False)


class UserProfileService():

    
    def __init__(self, request):
        self.request  = request


    def update_user_profile(self, data, user):

        try:
            member = user.member
            member.first_name = data['first_name']
            member.middle_name = data['middle_name']
            member.last_name = data['last_name']
            member.mobile_number = data['mobile_number']
            member.save()

            logger.info('Success, updating user profile: {}'.format(user.email))
            return ('', True, user)

        except Exception as e:
            log_error("Error updating user profile", e)
            return ('', False, None)
