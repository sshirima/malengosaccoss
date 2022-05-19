import threading
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from core.utils import print_error_message

from .utils import token_generator

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently= False)

class ActivationEmailSender():

    def __init__(self, request):
        self.request = request


    def send(self,subject, body, from_email, to, threading = True):
        try:
            email = EmailMessage(subject=subject,body=body, from_email=from_email, to=to)
            # email.send(fail_silently= False)

            if threading:
                EmailThread(email).start()
            else:
                email.send(fail_silently= False)
            return True
        except Exception as e:
            print_error_message("Error, Sending email", e)
            return False