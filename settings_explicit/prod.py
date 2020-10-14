"""
    PROD setting file
"""

from .base import *

print('Using prod.py as settings file')

DEBUG = False

ALLOWED_HOSTS = ['api.recruiting-analytics.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['POSTGRES_PROD_DATABASE'],
        'USER': config['POSTGRES_PROD_USER'],
        'PASSWORD': config['POSTGRES_PROD_PASSWORD'],
        'HOST': config['POSTGRES_PROD_DB_HOST'],
        'PORT': '5432',
    }
}
