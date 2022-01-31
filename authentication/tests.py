from lib2to3.pgen2 import token
from django.core import mail
from django.http import response
from django.test import TestCase
from django.urls.base import reverse
from django.contrib.auth.forms import PasswordChangeForm
import time

from authentication.forms import RegistrationForm
from .models import User
from .services import (
    PasswordResetService, 
    RegistrationService, 
    LoginService, 
    UserProfileService
    )
from .forms import (
    LoginForm, 
    PasswordResetChangeForm, 
    PasswordResetRequestForm, 
    RegistrationForm, 
    UserProfileUpdateForm)

# Create your tests here.

class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse('register'))
        self.invalid_registration_form = RegistrationForm(data={
            'first_name':'Samson',
            'last_name':'Shirima',
            'email':'emaildomain.com',
            'password1':'jimaya79',
            'password2':'jimaya792',
        })

        self.valid_registration_form =  RegistrationForm(data={
            'first_name':'Samson',
            'last_name':'Shirima',
            'email':'email@domain.com',
            'password1':'jimaya792',
            'password2':'jimaya792',
        })

        self.valid_login_form = LoginForm(data={
            'email':'email@domain.com',
            'password':'jimaya792',
        })

        self.invalid_login_form = LoginForm(data={
            'email':'emaildomain.com',
            'password':'',
        })

        self.valid_password_reset_form = PasswordResetRequestForm(data={
            'email':'email@domain.com',
        })

        self.invalid_password_reset_form = PasswordResetRequestForm(data={
            'email':'emaildomain.com',
        })
        self.valid_password_reset_change_form = PasswordResetChangeForm(data={
            'password1':'jimaya792',
            'password2':'jimaya792',
        })
        self.invalid_password_reset_change_form = PasswordResetChangeForm(data={
            'password1':'jimaya792',
            'password2':'jimaya',
        })

        

    def test_registration_form_errors(self):
        
        self.assertFalse(self.invalid_registration_form.is_valid())
        self.assertEqual(self.invalid_registration_form.errors['email'], ['Enter a valid email address.'])
        self.assertEqual(self.invalid_registration_form.errors['password2'], ['The two password fields didn’t match.'])
        

    def test_user_registration_success(self):
        
        registration_service = RegistrationService(self.response.wsgi_request)

        #Create user
        self.assertTrue(self.valid_registration_form.is_valid())

        created, user = registration_service.create_user(self.valid_registration_form.cleaned_data)
        self.assertTrue(created)
        self.assertIsNotNone(user)
    
    def test_registration_activation_link(self):
        #Send activation link via email
        registration_service = RegistrationService(self.response.wsgi_request)

        #Create user
        self.assertTrue(self.valid_registration_form.is_valid())

        created, user = registration_service.create_user(self.valid_registration_form.cleaned_data)
        
        activation_url = registration_service.create_activation_url(user)
        activation_link_sent = registration_service.send_activation_email(user, activation_url)
        self.assertTrue(activation_link_sent)
        self.assertEqual(len(mail.outbox), 1)

        #Activate user
        activation_url_split = activation_url.split('/')
        uidb64 = activation_url_split[5]
        token = activation_url_split[6]

        message, activated, user = registration_service.activate_user(uidb64, token)
        self.assertTrue(activated)
        self.assertTrue(user.is_active)

        #Reusing same activation link
        message, activated, usr = registration_service.activate_user(uidb64, token)
        self.assertFalse(activated)
        self.assertIsNone(usr)

        #Testing login
        #Send activation link via email
    def test_login_user(self):
        registration_service = RegistrationService(self.response.wsgi_request)
        self.assertTrue(self.valid_registration_form.is_valid())

        created, user = registration_service.create_user(self.valid_registration_form.cleaned_data)
        user.is_active = True
        user.save()

        loginservice = LoginService(self.response.wsgi_request)
        self.valid_login_form.is_valid()
        message, authenticated, user = loginservice.authenticate_user(self.valid_login_form.cleaned_data)
        self.assertTrue(authenticated)
        self.assertIsNotNone(user)

        #Testing password reset request
        resetService = PasswordResetService(self.response.wsgi_request)
        self.valid_password_reset_form.is_valid()
        user, password_reset_url = resetService.create_password_reset_url(self.valid_password_reset_form.cleaned_data)
        self.assertIsNotNone(user)

        email_sent = resetService.send_password_reset_email(user, password_reset_url)
        self.assertTrue(email_sent)

        password_reset_url_split = password_reset_url.split('/')
        uidb642 = password_reset_url_split[5]
        token2 = password_reset_url_split[6]
        

        token_valid = resetService.check_token_validity(uidb642, token2)
        self.assertTrue(token_valid)

        self.valid_password_reset_change_form.is_valid()
        reset_password = resetService.reset_password(uidb642, self.valid_password_reset_change_form.cleaned_data)
        self.assertTrue(reset_password)

        invalid_token_valid = resetService.check_token_validity(uidb642, token2)
        self.assertFalse(invalid_token_valid)




    def test_login_form_success(self):
        is_valid = self.valid_login_form.is_valid()
        self.assertTrue(is_valid)

    def test_login_form_errors(self):
        is_valid = self.invalid_login_form.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(self.invalid_login_form.errors['email'], ['Enter a valid email address.'])
        self.assertEqual(self.invalid_login_form.errors['password'], ['This field is required.'])

    def test_password_reset_form_success(self):
        is_valid = self.valid_password_reset_form.is_valid()
        self.assertTrue(is_valid)

    def test_password_reset_form_errors(self):
        is_valid = self.invalid_password_reset_form.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(self.invalid_password_reset_form.errors['email'], ['Enter a valid email address.'])
    
    def test_password_reset_change_form_success(self):
        is_valid = self.valid_password_reset_change_form.is_valid()
        self.assertTrue(is_valid)

    def test_password_reset_change_errors(self):
        is_valid = self.invalid_password_reset_change_form.is_valid()
        self.assertFalse(is_valid)
        self.assertIn('The two password fields didn’t match.', str(self.invalid_password_reset_change_form.errors))


    def test_password_change_form_success(self):
        registration_service = RegistrationService(self.response.wsgi_request)
        created, user = registration_service.create_user(data={
            'first_name':'Stephen',
            'last_name':'Shirima',
            'email':'email2@domain.com',
            'password1':'jimaya792',
            'password2':'jimaya792',
            'mobile_number':'',
        })
        
        valid_password_change_form = PasswordChangeForm(user=user, data={
            'old_password':'jimaya792',
            'new_password1':'anotherPwd792',
            'new_password2':'anotherPwd792',
        })

        is_valid = valid_password_change_form.is_valid()
        print(valid_password_change_form.errors)
        self.assertTrue(is_valid)

    
    def test_password_change_errors(self):
        registration_service = RegistrationService(self.response.wsgi_request)
        created, user = registration_service.create_user(data={
            'first_name':'Stephen',
            'last_name':'Shirima',
            'email':'email2@domain.com',
            'password1':'jimaya792',
            'password2':'jimaya792',
            'mobile_number':'',
        })
        
        invalid_password_change_form = PasswordChangeForm(user=user, data={
            'old_password':'jimaya792',
            'new_password1':'jim792',
            'new_password2':'anotherPwd792',
        })

        is_valid = invalid_password_change_form.is_valid()
        self.assertFalse(is_valid)
        self.assertIn('The two password fields didn’t match.', str(self.invalid_password_reset_change_form.errors))


    def test_update_user_profile_success(self):
        registration_service = RegistrationService(self.response.wsgi_request)
        created, user = registration_service.create_user(data={
            'first_name':'Stephen',
            'last_name':'Shirima',
            'email':'email2@domain.com',
            'password1':'jimaya792',
            'password2':'jimaya792',
            'mobile_number':'',
        })
        
        valid_user_profile_form = UserProfileUpdateForm (data={
            'first_name':'Samson',
            'last_name':'Shirima',
            'mobile_number':'255754711711',
        })

        is_valid = valid_user_profile_form.is_valid()
        self.assertTrue(is_valid)
        
        up_service = UserProfileService(self.response.wsgi_request)

        result, updated, user = up_service.update_user_profile(valid_user_profile_form.cleaned_data, user)

        self.assertTrue(updated)
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Samson')
        self.assertEqual(user.last_name, 'Shirima')
        self.assertEqual(user.mobile_number, '255754711711')

        invalid_user_profile_form = UserProfileUpdateForm (data={
            'first_name':'Samson',
            'last_name':'',
            'mobile_number':'',
        })

        is_valid = invalid_user_profile_form.is_valid()
        self.assertTrue(is_valid)
        print(invalid_user_profile_form.errors)


    # def test_login_success(self):
    #     loginservice = LoginService(self.response.wsgi_request)
    #     self.valid_login_form.is_valid()
    #     message, authenticated, user = loginservice.authenticate_user(self.valid_login_form.cleaned_data)
    #     self.assertTrue(authenticated)
    #     self.assertIsNotNone(user)
        
    
#     def test_registration_view_get(self):
#         """
#         test template_used
#         test form used
#         """
#         response = self.client.get(reverse('register'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'authentication/register.html')


#     def test_registration_view_post_success(self):
#         """
#         test data validation
#         test error messages displayed
#         """
#         response = self.client.post(reverse('register'), data={
#             'username':'sshirima',
#             'first_name':'Samson',
#             'last_name':'Shirima',
#             'email':'email@domain.com',
#             'password1':'jimaya792',
#             'password2':'jimaya792',

#         })

#         self.assertRedirects(response, reverse('login'))
        
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, reverse('login'))

#         self.assertEqual(len(mail.outbox), 1)

#     def test_registration_view_post_fail(self):
#         """
#         test data validation
#         test error messages displayed
#         """
#         response = self.client.post(reverse('register'), data={
#             'username':'',
#             'first_name':'Samson',
#             'last_name':'Shirima',
#             'email':'email@domaincom',
#             'password1':'jimaya79',
#             'password2':'jimaya792',

#         })

#         #self.assertRedirects(response, 'http://127.0.0.1%s'%reverse('login'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'authentication/register.html')
#         self.assertIsInstance(response.context['form'], RegistrationForm)
#         self.assertIn('This field is required', str(response.context['form'].errors))
#         self.assertIn('The two password fields didn', str(response.context['form'].errors))
#         self.assertIn('Enter a valid email address.', str(response.context['form'].errors))
        
#         #self.assertEqual(len(mail.outbox), 1)


# class LoginViewTestCase(TestCase):

#     def test_login_view_get(self):
#         """
#         test template_used
#         test form used
#         """
#         response = self.client.get(reverse('login'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'authentication/login.html')

#     def test_login_view_post_success(self):
#         """
#         test response code
#         test redirection
#         """
#         response = self.client.post(reverse('register'), data={
#             'username':'sshirima',
#             'first_name':'Samson',
#             'last_name':'Shirima',
#             'email':'email@domain.com',
#             'password1':'jimaya792',
#             'password2':'jimaya792',

#         })

#         # user = User.objects.get(email='email@domain.com')
#         # user.is_active = True
#         # user.save()
        
#         response1 = self.client.post(reverse('login'), data={
#             'email':'email@domain.com',
#             'password':'jimaya792',
#         })

#         # user = User.objects.get(email='email@domain.com')
#         # self.assertIsNotNone(user)
#         #self.assertEqual(response.status_code, 302)
#         #self.assertRedirects(response, reverse('dashboard'))
        


