
from builtins import Exception, print
from django.core.management.base import BaseCommand
from members.models import Member
import pandas as pd
from django.db import transaction
from django.conf import settings

from authentication.services import RegistrationService
from core.utils import log_error

class Command(BaseCommand):

    def handle(self,  *args, **kwargs):
        self.stdout.write('Adding member accounts from csv file....')
        try:
            BASE_DIR = settings.BASE_DIR
            members_file = BASE_DIR / 'static/init/members.csv'

            df_members = pd.read_csv(members_file,skipinitialspace=True, header=0,skip_blank_lines=True)
            df_members.columns = df_members.columns.str.strip()

            with transaction.atomic():
                for index, row in df_members.iterrows():
                    registrationService = RegistrationService()

                    created, u = registrationService.create_user(
                        email=row['email'],
                        password1='Changeme_123',
                        first_name=row['first_name'],
                        middle_name=row['middle_name'],
                        last_name=row['last_name'],
                        mobile_number=row['mobile_number'],
                        gender=row['gender'],
                        password_change = True,
                        is_active = True
                    )
                    if created:
                        print('{}: Success, Member created: {}'.format(index, row['email']))
                        continue
                    print('Error, user creation fails')

        except Exception as e:
            log_error("Error, adding member command", e)
        
        

        