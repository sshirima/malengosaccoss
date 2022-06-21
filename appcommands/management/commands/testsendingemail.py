
from django.core.management.base import BaseCommand
from django.conf import settings

from core.utils import log_error, SmtpEmailSender

class Command(BaseCommand):
    help = "Clearing all data on the database ..."

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('poll_ids', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument('-t', '--threading', action='store_true', help='Use threading to send email')

    def handle(self, *args, **kwargs):
        self.stdout.write('Sending test email ....')
        try:
            threading = kwargs['threading']

            email_sender = settings.DEFAULT_FROM_EMAIL
            emaisender = SmtpEmailSender()
            is_sent = emaisender.send(
                threading=threading,
                subject='Testing message from malengosaccos app',
                body='This is the testing body', 
                from_email=email_sender, 
                to=['malengosaccosapp@gmail.com']
            )
            if is_sent:
                self.stdout.write('Exit code 0, success')
            else:
                self.stdout.write('Exit code 1, fail')
        except Exception as e:
            log_error("ERROR, sending testing email", e)
            self.stdout.write('Exit code 2, fail')

        