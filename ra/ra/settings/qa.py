"""
    Qa setting file
"""

from .base import *

print('Using qa.py as settings file')

DEBUG = True

ALLOWED_HOSTS = ['qa-api.recruiting-analytics.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['POSTGRES_QA_DATABASE'],
        'USER': config['POSTGRES_USER'],
        'PASSWORD': config['POSTGRES_PASSWORD'],
        'HOST': config['POSTGRES_DB_HOST'],
        'PORT': '5432',
    }
}
