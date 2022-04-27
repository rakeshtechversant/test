"""
Django settings for church_project project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import dj_database_url
from datetime import timedelta

env = os.environ.copy()
DB_URL = env.get('DATABASE_URL', False)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tpl3m7ut2t=xvnm$so@p-ma1ps8q&jol6_w%%#_u-e#!g^lktk'

# SECURITY WARNING: don't run with debug turned on in production!

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'import_export',
    'ckeditor',
    "push_notifications",
    #project app
    'apps.church',
    'apps.api'
]

PUSH_NOTIFICATIONS_SETTINGS = {
        "FCM_API_KEY": "AAAA1gbkJM0:APA91bEY8L23AzHx9as00rLjO8ckJk93-2C_mlIfwD90HGi8ePjqsQcz7kRynjc02crnPR4k0PKrFomPkcNybpXxzgRbGPrlK8do4T3Rgb7dMExbvynQJahYGAOjPuwgDWPtsjFZxeRc",
        "GCM_API_KEY": "AAAA1gbkJM0:APA91bEY8L23AzHx9as00rLjO8ckJk93-2C_mlIfwD90HGi8ePjqsQcz7kRynjc02crnPR4k0PKrFomPkcNybpXxzgRbGPrlK8do4T3Rgb7dMExbvynQJahYGAOjPuwgDWPtsjFZxeRc",
        # "APNS_CERTIFICATE": os.path.join(BASE_DIR, "pushcert.pem"),
        # "APNS_TOPIC": "com.example.push_test",
        "WNS_PACKAGE_SECURITY_ID": "[your package security id, e.g: 'ms-app://e-3-4-6234...']",
        "WNS_SECRET_KEY": "[your app secret key, e.g.: 'KDiejnLKDUWodsjmewuSZkk']",
        "WP_PRIVATE_KEY": "/path/to/your/private.pem",
        "WP_CLAIMS": {'sub': "mailto: development@example.com"}
}

PUSH_NOTIFICATIONS_SETTINGS = {
  # Load and process all PUSH_NOTIFICATIONS_SETTINGS using the AppConfig manager.
  "CONFIG": "push_notifications.conf.AppConfig",

  # collection of all defined applications
  "APPLICATIONS": {
    "com.techversant.paulschurchapp": {
      # PLATFORM (required) determines what additional settings are required.
      "PLATFORM": "FCM",
      "API_KEY" : "AAAA1gbkJM0:APA91bEY8L23AzHx9as00rLjO8ckJk93-2C_mlIfwD90HGi8ePjqsQcz7kRynjc02crnPR4k0PKrFomPkcNybpXxzgRbGPrlK8do4T3Rgb7dMExbvynQJahYGAOjPuwgDWPtsjFZxeRc",
    },
    "com.techversant.MukhathalaMarThomaChurch":{
        "PLATFORM": "APNS",
        "CERTIFICATE": os.path.join(BASE_DIR, "apns-dev-cert.pem"),
        "TOPIC" : "com.techversant.MukhathalaMarThomaChurch",
    }
  }
}

UPDATE_ON_DUPLICATE_REG_ID = True
# JET_DEFAULT_THEME = 'green'
# JET_THEMES = [
#     {
#         'theme': 'default', # theme folder name
#         'color': '#47bac1', # color of the theme's button in user menu
#         'title': 'Default' # theme title
#     },
#     {
#         'theme': 'green',
#         'color': '#30a093',
#         'title': 'Green'
#     },
#     {
#         'theme': 'light-green',
#         'color': '#2faa60',
#         'title': 'Light Green'
#     },
#     {
#         'theme': 'light-violet',
#         'color': '#a464c4',
#         'title': 'Light Violet'
#     },
#     {
#         'theme': 'light-blue',
#         'color': '#5EADDE',
#         'title': 'Light Blue'
#     },
#     {
#         'theme': 'light-gray',
#         'color': '#222',
#         'title': 'Light Gray'
#     }
# ]
# JET_CHANGE_FORM_SIBLING_LINKS = True


REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    #'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'church_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join (BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'church_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


if DB_URL != False:
    DATABASES = {
    'default': {
   'ENGINE': 'django.db.backends.postgresql_psycopg2',
    },
    }

    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)
    DEBUG = True
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    DEBUG = True

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE =  'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#jwt
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# Twilio Configuration
TWILIO_ACCOUNT_SID = 'AC924f53fd86c176e97396b610668167e1'
TWILIO_AUTH_TOKEN = '1885823752ba0fb3c49a81aeba59a851'
DJANGO_TWILIO_FORGERY_PROTECTION = False
DJANGO_TWILIO_BLACKLIST_CHECK = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/cards/'

MEDIA_ROOT = os.path.join(BASE_DIR, "cards")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

FILE_UPLOAD_PERMISSIONS = 0O644
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# CKEDITOR_BASEPATH =STATIC_ROOT + "/ckeditor/ckeditor/"
DEFAULT_DOMAIN = "http://202.88.246.92:8014"
