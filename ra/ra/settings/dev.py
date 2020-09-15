"""
    Dev setting file
"""

from .base import *

print('Using local.py as settings file')

DEBUG = True

ALLOWED_HOSTS = ['18.189.28.11', 'dev-api.recruiting-analytics.com',]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['POSTGRES_DEV_DATABASE'],
        'USER': config['POSTGRES_USER'],
        'PASSWORD': config['POSTGRES_PASSWORD'],
        'HOST': config['POSTGRES_DB_HOST'],
        'PORT': '5432',        
    }
}