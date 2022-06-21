from datetime import datetime
from django.conf import settings
import pandas as pd
import re
from core.utils import log_error
from datetime import datetime
from operator import itemgetter

class LogsfileParser():

    pattern_logline = None
    pattern_logtext = None
    
    def __init__(self, filepath, **kwargs) -> None:
        self.filepath = filepath
        self.pattern_logline = re.compile('\[%(.*?)%\]',  re.IGNORECASE)
        self.pattern_logtext = re.compile('^(.*?)\s(.*?\s.*?\s)(.*)',  re.IGNORECASE)

    def query_log_from_request(self, request):
        sortby = request.GET.get('sort') if request.GET.get('sort') else ''

        """
        Sorting ascending descending per field
        """
        if  sortby in ['level','message','time','-level','-message','-time']:
            descending = True if sortby.startswith('-') else False   
            sortby = sortby.replace('-','') if descending else sortby

        else:
            sortby = 'time'
            descending = False

        """
        Extract the filters from the request
        """
        filters = {}
        level = request.GET.get('level') if request.GET.get('level') else ''
        message = request.GET.get('message') if request.GET.get('message') else ''
        starttime = request.GET.get('starttime') if request.GET.get('starttime') else None
        endtime = request.GET.get('endtime') if request.GET.get('endtime') else None

        if not level == '':
            filters['level'] = level

        if not message == '':
            filters['message'] = message

        if starttime:
            filters['starttime'] = datetime.strptime(starttime, '%Y-%m-%d')


        if endtime:
            filters['endtime'] = datetime.strptime(endtime, '%Y-%m-%d')

        return self.query_logs_file(sortby=sortby, descending=descending, **filters)



    def query_logs_file(self,sortby='time', descending=False, **filters):
        
        linenumber = 0
        stacktrace = ''
        stack_length = 1
        logsdata = []

        try:
            with open (self.filepath, 'rt') as logfile:  
                for line in logfile:
                    linenumber+=1

                    if self.pattern_logline.search(line) != None:
                        
                        if not stacktrace == '' and logsdata:

                            last_lognumber = int(logsdata[-1]['linenumber'])

                            if linenumber == last_lognumber+stack_length:
                                logsdata[-1]['stacktrace'] = stacktrace

                        stacktrace = ''
                        stack_length =1
                        linetext = line.strip('\n').strip('\[%').strip('%\]')

                        extracted = self.pattern_logtext.search(linetext)
                        extracted_object = self._get_logs_information_as_dict(extracted, linenumber=linenumber)

                        passed_filters = self._check_filters(('level', 'message','starttime', 'endtime'), filters)
                        if  not  passed_filters:
                            #No filter
                            logsdata.append(extracted_object)
                            continue

                        pass_condition  = False
                        key_count = 0

                        for key in passed_filters:
                            filter_value = filters[key]
                            filter_condition = False

                            if 'starttime' == key:
                                str_logtime = extracted.group(2).split(',')[0]
                                logtime = datetime.strptime(str_logtime, '%Y-%m-%d %H:%M:%S')
                                filter_condition =  filter_value <= logtime

                            if 'endtime' == key:
                                str_logtime = extracted.group(2).split(',')[0]
                                logtime = datetime.strptime(str_logtime, '%Y-%m-%d %H:%M:%S')
                                filter_condition =  logtime <= filter_value
                            
                            if 'level' == key or 'message' == key:
                                filter_condition = filter_value.lower() in extracted_object[key].lower()

                            if key_count == 0:
                                pass_condition = filter_condition
                            else:
                                pass_condition = pass_condition and filter_condition

                            key_count += 1

                        if pass_condition:
                            logsdata.append(extracted_object)

                        continue

                    stacktrace += line
                    stack_length += 1


        except Exception as e:
            log_error("Error, parsing logs file", e)
            return []

        logsdata = sorted(logsdata, key=itemgetter(sortby), reverse=descending) 

        return logsdata

    def _check_filters(self, available_filters, passed_fitlers):
        return_filters = []
        for f in passed_fitlers:
            if f in available_filters:
                return_filters.append(f)
        return return_filters


    def _get_logs_information_as_dict(self, regex_object, **kwargs):
        
        return {
            'linenumber':kwargs['linenumber'],
            'level':regex_object.group(1),
            'time':regex_object.group(2),
            'message':regex_object.group(3),
            'stacktrace':''
            }
        

    def get_logs_by_level(self, level):
        linenumber = 0
        stacktrace = ''
        stack_length = 1
        logsdata = []
        try: 
            with open (self.filepath, 'rt') as logfile:  
                for line in logfile:
                    linenumber+=1
                    if self.pattern_logline.search(line) != None:
                    
                        if not stacktrace == '' and logsdata:

                            last_lognumber = int(logsdata[-1]['linenumber'])

                            if linenumber == last_lognumber+stack_length:
                                logsdata[-1]['stacktrace'] = stacktrace

                            stacktrace = ''
                            stack_length =1

                        linetext = line.strip('\n').strip('\[%').strip('%\]')

                        if level.lower() in linetext.lower():
                            extracted = self.pattern_logtext.search(linetext)
                            extracted_object = self._get_logs_information_as_dict(extracted, linenumber=linenumber)
                            logsdata.append(extracted_object)

                        continue
                    stacktrace += line
                    stack_length+=1

        except Exception as e:
            log_error("Error, parsing logs file", e)
            return []

        return logsdata

    def get_logs_by_message(self, message):
        linenumber = 0
        stacktrace = ''
        stack_length = 1
        logsdata = []
        try:
            with open (self.filepath, 'rt') as logfile:  
                for line in logfile:
                    linenumber+=1
                    if self.pattern_logline.search(line) != None:
                        

                        if not stacktrace == '' and logsdata:

                            last_lognumber = int(logsdata[-1]['linenumber'])

                            if linenumber == last_lognumber+stack_length:
                                logsdata[-1]['stacktrace'] = stacktrace

                            stacktrace = ''
                            stack_length =1

                        linetext = line.strip('\n').strip('\[%').strip('%\]')

                        if message.lower() in linetext.lower():
                            extracted = self.pattern_logtext.search(linetext)
                            extracted_object = self._get_logs_information_as_dict(extracted, linenumber=linenumber)
                            logsdata.append(extracted_object)

                        continue

                    stacktrace += line
                    stack_length+=1


        except Exception as e:
            log_error("Error, parsing logs file", e)
            return []

        return logsdata

    def get_logs_by_time(self, start_time, end_time):
        linenumber = 0
        stacktrace = ''
        stack_length = 1
        logsdata = []
        try:
            with open (self.filepath, 'rt') as logfile:  
                for line in logfile:
                    linenumber+=1
                    if self.pattern_logline.search(line) != None:
                        

                        if not stacktrace == '' and logsdata:

                            last_lognumber = int(logsdata[-1]['linenumber'])

                            if linenumber == last_lognumber+stack_length:
                                logsdata[-1]['stacktrace'] = stacktrace

                            stacktrace = ''
                            stack_length =1

                        linetext = line.strip('\n').strip('\[%').strip('%\]')
                        extracted = self.pattern_logtext.search(linetext)
                        str_logtime = extracted.group(2).split(',')[0]
                        logtime = datetime.strptime(str_logtime, '%Y-%m-%d %H:%M:%S')

                        if start_time <= logtime <= end_time:
                            extracted_object = self._get_logs_information_as_dict(extracted, linenumber=linenumber)
                            logsdata.append(extracted_object)
                            
                        continue
                    stacktrace += line
                    stack_length+=1

        except Exception as e:
            log_error("Error, parsing logs file", e)
            return []

        return logsdata