from django.conf import settings # import the settings file

def application_name(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'APP_NAME': settings.APP_NAME}