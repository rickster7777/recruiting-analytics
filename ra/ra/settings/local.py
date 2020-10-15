"""
    Local setting file
    Please create new file named as local.py and
    copy contents of this file into local.py    Please do not change this file local.py.rename to local.py
"""

from .base import *
print('Using local.py as settings file')
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1',]
#ALLOWED_HOSTS = ['127.0.0.1','qa-api.recruiting-analytics.com',]
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'local',
#         'USER': 'local',
#         'PASSWORD': 'pass',
#         'HOST': '172.17.0.2',
#         'PORT': '5432',
#     }
# }
# 'NAME': config['POSTGRES_DEV_DATABASE'],
        # 'USER': config['POSTGRES_USER'],
        # 'PASSWORD': config['POSTGRES_PASSWORD'],
        # 'HOST':  'ra-db.cw4nxhdibxun.us-east-2.rds.amazonaws.com',
        # 'PORT': '5432',

# ALLOWED_HOSTS = ['127.0.0.1:8000', 'dev-api.recruiting-analytics.com', '*']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}