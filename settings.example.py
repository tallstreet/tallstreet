# -*- coding: utf-8 -*-
from appenginepatcher import on_production_server
import os
DEBUG = not on_production_server
#DEBUG = True
ENABLE_PROFILER = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'appengine'

MEDIA_URL = '/media/'

# Email server settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'user'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'user@localhost'
SERVER_EMAIL = 'user@localhost'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'ragendja.template.app_prefixed_loader',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'ragendja.middleware.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'ts.urls'
AUTH_USER_MODULE = 'ts.traders.usermodel'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.webdesign',
    'appenginepatcher',
    'ts.search',
    'ts.traders',
    'templatetags',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

LOGIN_URL = "/login.html"
LOGIN_REDIRECT_URL = "/account/"

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

#LOGIN_REQUIRED_PREFIXES = (
#    'account/'
#)
NO_LOGIN_REQUIRED_PREFIXES = (
    'login.html'
)


TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

CACHE_BACKEND = 'memcached://?timeout=0'

DJANGO_STYLE_MODEL_KIND = False


FACEBOOK_API_KEY = ''
FACEBOOK_API_SECRET = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = '123'
RECAPTCHA_PUB_KEY = "123"
RECAPTCHA_PRIVATE_KEY = "123"

