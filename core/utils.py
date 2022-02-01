
from datetime import datetime

def get_formated_date(datetime, format):
    
    return datetime.strftime(datetime, format)