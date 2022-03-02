from .settings import *

DEBUG = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'mturk_management',
    'USER': 'postgres',
    'PASSWORD': os.environ.get('MONGO_PASSWORD'),
    'HOST': 'davidz.cn',
    'PORT': '5432'
}

ALLOWED_HOSTS = ['mturk.davidz.cn']
