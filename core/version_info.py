# core/version_info.py
from django.conf import settings

def app_info(request):
    return {
        'APP_VERSION': settings.APP_VERSION, 
        'APP_AUTHOR': settings.APP_AUTHOR,
        'APP_DATE': settings.APP_DATE,
        'APP_EMAIL': settings.APP_EMAIL, 
        'APP_DESCRIPTION': settings.APP_DESCRIPTION,
    }
