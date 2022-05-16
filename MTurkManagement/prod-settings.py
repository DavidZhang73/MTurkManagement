from .settings import *

DEBUG = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'mturk_management',
    'USER': os.environ.get('POSTGRESQL_USER'),
    'PASSWORD': os.environ.get('POSTGRESQL_PASSWORD'),
    'HOST': os.environ.get('POSTGRESQL_HOST'),
    'PORT': os.environ.get('POSTGRESQL_PORT'),
}

ALLOWED_HOSTS = ['mturk.davidz.cn', 'vidat.cecs.anu.edu.au:8000']
