"""
Django settings for MTurkManagement project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-rp+qk@l%+=ic1(-$!2zc-dyqd&ggn*3kejapxugek8em11nb53'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django_monaco_editor',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'import_export',
    'item',
    'task'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MTurkManagement.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('template')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'MTurkManagement.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
    'mongo': {
        'ENGINE': 'djongo',
        'NAME': 'IkeaAssemblyInstruction',
        'CLIENT': {
            'host': 'davidz.cn:27017',
            'username': 'david',
            'password': os.environ.get('MONGO_PASSWORD')
        }
    }
}

DATABASE_ROUTERS = ('MTurkManagement.dbrouters.DBRouter',)

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Sydney'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORs Headers
# https://github.com/adamchainz/django-cors-headers
CORS_ALLOWED_ORIGINS = [
    "http://localhost:63344",
    "http://127.0.0.1:63344",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://vidat.davidz.cn",
    "https://vidat2.davidz.cn",
]

# Simple UI
# https://simpleui.72wo.com/docs/simpleui/quick.html
SIMPLEUI_HOME_PAGE = '/home/'
SIMPLEUI_HOME_TITLE = 'Home'
SIMPLEUI_HOME_ICON = 'fas fa-home'
SIMPLEUI_ANALYSIS = False
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menus': [
        {
            'app': 'task',
            'name': 'MTurk',
            'icon': 'fas fa-pencil-ruler',
            'models': [
                {
                    'name': 'Batch',
                    'icon': 'fas fa-clipboard-list',
                    'url': 'task/batch/'
                },
                {
                    'name': 'Task',
                    'icon': 'fas fa-tasks',
                    'url': 'task/task/'
                },
                {
                    'name': 'Submission',
                    'icon': 'fas fa-file-upload',
                    'url': 'task/submission/'
                },
                {
                    'name': 'Audit',
                    'icon': 'fas fa-clipboard-check',
                    'url': 'task/audit/'
                },
                {
                    'name': 'Settings',
                    'icon': 'fas fa-cog',
                    'url': 'task/settings/'
                }
            ]
        },
        {
            'app': 'item',
            'name': 'Dataset',
            'icon': 'fa fa-database',
            'models': [
                {
                    'name': 'Category',
                    'icon': 'fa fa-filter',
                    'url': 'item/category/'
                },
                {
                    'name': 'Item',
                    'icon': 'fa fa-couch',
                    'url': 'item/item/'
                }
            ]
        },
        {
            'app': 'auth',
            'name': 'Authentication',
            'icon': 'fa fa-user-shield',
            'models': [
                {
                    'name': 'User',
                    'icon': 'fa fa-user',
                    'url': 'auth/user/'
                },
                {
                    'name': 'Group',
                    'icon': 'fa fa-users-cog',
                    'url': 'auth/group/'
                }
            ]
        }
    ]
}
