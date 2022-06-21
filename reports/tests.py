from django.test import TestCase
from datetime import datetime
from django.conf import settings
# Create your tests here.
from reports.services import LogsfileParser


class TestDjangoLogviewer(TestCase):
    basedir = BASE_DIR = settings.BASE_DIR 
    filepath = basedir / 'logs/application' / 'logs.log'
    reader = LogsfileParser(filepath)
    # logs_data = reader.query_logs_file(level='err', message='inter')
    # logs_data = reader.get_logs_by_level( 'err')
    # logs_data = reader.get_logs_by_message('server')
    starttime = datetime.strptime('2022-06-01 19:00:00', '%Y-%m-%d %H:%M:%S')
    endtime = datetime.strptime('2022-06-01 23:00:00', '%Y-%m-%d %H:%M:%S')
    logs_data = reader.query_logs_file(sortby='level', descending=True,starttime =starttime, endtime=endtime)
    print(logs_data)