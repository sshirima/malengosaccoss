
from datetime import datetime

def get_formated_date(datetime, format):
    
    return datetime.strftime(datetime, format)

def get_filename_with_timestamps(name):
    if name is None:
        name = 'file'
    now = datetime.now()
    return '{}_{}_{}_{}_{}.csv'.format(name, now.year, now.month, now.day, str(now.hour)+str(now.minute)+str(now.second))