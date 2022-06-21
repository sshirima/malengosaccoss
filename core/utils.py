
from datetime import datetime
from django.core.mail import EmailMessage
import threading
import logging

logger = logging.getLogger(__name__)

def get_formated_date(datetime, format):
    
    return datetime.strftime(datetime, format)

def get_filename_with_timestamps(name):
    if name is None:
        name = 'file'
    now = datetime.now()
    return '{}_{}_{}_{}_{}.csv'.format(name, now.year, now.month, now.day, str(now.hour)+str(now.minute)+str(now.second))

def get_timestamps_filename(now=None, name='file'):
    now = datetime.now() if now is None else now
    return '{}_{}_{}_{}_{}'.format(now.year, now.month, now.day, str(now.hour)+str(now.minute)+str(now.second), name)

def get_exception_error_message(message, e):
    return '{}: file {}, line {}: {}'.format(message, e.__traceback__.tb_frame.f_code.co_filename, e.__traceback__.tb_lineno, str(e))    
    
def log_error(message, e):
    error_message = get_exception_error_message(message, e)
    logger.error(error_message)
    print(error_message)


class SmtpEmailSenderThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send(fail_silently= False)
        except Exception as e:
            log_error("ERROR, Sending email", e)


class SmtpEmailSender():

    def send(self, threading = False, **kwargs):
        try:
            email = EmailMessage(
                subject=kwargs['subject'],
                body=kwargs['body'], 
                from_email=kwargs['from_email'], 
                to=kwargs['to']
            )
            if threading:
                SmtpEmailSenderThread(email).start()
            else:
                email.send(fail_silently= False)
            return True
        except Exception as e:
            log_error("ERROR, Sending email", e)
            return False