# -*- coding: utf-8 -*-
import django, sys, os
from django.conf import settings

SECRET_KEY = '--'
BASE_DIR = os.path.dirname(__file__)

DEBUG=True

DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS=(
    'django.contrib.sites',
    'payments',

    'tests'
)
