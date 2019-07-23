"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'abwg#ajfesa+5qw^q4basopg0y5)duny*=l-k$wl^=u6bp(xqx'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['10.1.50.1','10.68.140.15','127.0.0.1','10.68.2.38',"192.168.43.94"] 

# Application definition

INSTALLED_APPS = [
    'muradefect.apps.MuradefectConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'muradefect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.static',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

#DATABASES = {
#    'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'ppa',
#         'USER': 'k2data',
#         'PASSWORD': 'K2data1234',
#         'HOST': '10.68.2.182',
#         'PORT': '30012',
#         #'CONN_MAX_AGE': 5,
#     }
#}
    
DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'ppa',
         'USER': 'root',
         'PASSWORD': 'root',
         'HOST': '127.0.0.1',
         'PORT': '5432',
         'CONN_MAX_AGE': 5,
     }
}


#DATABASES = {
#    'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'k2data',
#         'USER': 'k2data',
#         'PASSWORD': 'K2data1234',
#         'HOST': '49.4.71.110',
#         'PORT': '30012',
#         #'CONN_MAX_AGE': 5,
#     }
#}


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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

#setting.py 增加以下配置
STATIC_URL = '/static/'
HERE=os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT =os.path.join( HERE , 'static').replace('\\','/')
STATICFILES_DIRS = (
("assets", os.path.join(STATIC_ROOT,'images').replace('\\','/')),
("css", os.path.join(STATIC_ROOT,'css').replace('\\','/')),
("js", os.path.join(STATIC_ROOT,'js').replace('\\','/')),
)
#urls.py 增加以下配置
