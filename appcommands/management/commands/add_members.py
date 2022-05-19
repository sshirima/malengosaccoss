
from builtins import Exception, print
from django.core.management.base import BaseCommand
from members.models import Member
import pandas as pd
from django.db import transaction

from authentication.services import RegistrationService
from core.utils import print_error_message

class Command(BaseCommand):

    def handle(self,  *args, **kwargs):
        self.stdout.write('Adding member accounts from csv file....')
        try:
            df_members = pd.read_csv('static/init/members.csv',skipinitialspace=True, header=0,skip_blank_lines=True)
            df_members.columns = df_members.columns.str.strip()

            with transaction.atomic():
                for index, row in df_members.iterrows():
                    registrationService = RegistrationService()

                    created, user = registrationService.create_user(
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
                        print('Success, Member created: {}'.format(user.email))
                        continue
                    print('Error, user creation fails')

        except Exception as e:
            print_error_message("Error, adding member command", e)
        
        

        