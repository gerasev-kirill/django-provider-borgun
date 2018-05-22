# -*- coding: utf-8 -*-
import django, sys, os
from django.conf import settings

SECRET_KEY = '--'
BASE_DIR = os.path.dirname(__file__)
ALLOWED_HOSTS = ['*']

TEST_HOSTNAME = "7e1b539d.ngrok.io"

DEBUG=True

INSTALLED_APPS=(
    'django.contrib.sites',
    'payments',

    'tests'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
    }
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True
    }
]
ROOT_URLCONF='tests.urls'

PAYMENT_HOST = 'localhost:8000'
PAYMENT_USES_SSL = True
PAYMENT_MODEL = 'tests.Payment'
PAYMENT_VARIANTS = {
    'default': ('payments_borgun.BorgunProvider', {
        'sandbox': True
    })
}
