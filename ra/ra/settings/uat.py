"""
    Staging setting file
"""

from .base import *

print('Using staging.py as settings file')

DEBUG = False

ALLOWED_HOSTS = ['uat-api.recruiting-analytics.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['POSTGRES_UAT_DATABASE'],
        'USER': config['POSTGRES_USER'],
        'PASSWORD': config['POSTGRES_PASSWORD'],
        'HOST': config['POSTGRES_DB_HOST'],
        'PORT': '5432',
    }
}
