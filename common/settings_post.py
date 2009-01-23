# -*- coding: utf-8 -*-
from settings import *

if '%d' in MEDIA_URL:
    MEDIA_URL = MEDIA_URL % MEDIA_VERSION
if '%s' in ADMIN_MEDIA_PREFIX:
    ADMIN_MEDIA_PREFIX = ADMIN_MEDIA_PREFIX % MEDIA_URL

TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS

# You can override Django's or some apps' locales with these folders:
if os.path.exists(os.path.join(COMMON_DIR, 'locale_overrides_common')):
    INSTALLED_APPS += ('locale_overrides_common',)
if os.path.exists(os.path.join(PROJECT_DIR, 'locale_overrides')):
    INSTALLED_APPS += ('locale_overrides',)

# Add admin interface media files if necessary
if 'django.contrib.admin' in INSTALLED_APPS:
    INSTALLED_APPS += ('django_aep_export.admin_media',)

# Always add Django templates (exported from zip)
INSTALLED_APPS += (
    'django_aep_export.django_templates',
)

# Add start markers, so apps can insert JS/CSS at correct position
def add_app_media(env, combine, *appmedia):
    COMBINE_MEDIA = env['COMBINE_MEDIA']
    COMBINE_MEDIA.setdefault(combine, ())
    if '!START!' not in COMBINE_MEDIA[combine]:
        COMBINE_MEDIA[combine] = ('!START!',) + COMBINE_MEDIA[combine]
    index = list(COMBINE_MEDIA[combine]).index('!START!')
    COMBINE_MEDIA[combine] = COMBINE_MEDIA[combine][:index] + \
        appmedia + COMBINE_MEDIA[combine][index:]

def add_uncombined_app_media(env, app):
    """Copy all media files directly"""
    path = os.path.join(
        os.path.dirname(__import__(app, {}, {}, ['']).__file__), 'media')
    app = app.rsplit('.', 1)[-1]
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.css', '.js')):
                base = os.path.join(root, file)[len(path):].replace(os.sep,
                    '/').lstrip('/')
                target = '%s/%s' % (app, base)
                add_app_media(env, target, target)

# Import app-specific settings
for app in INSTALLED_APPS:
    try:
        data = __import__(app + '.settings', {}, {}, [''])
        for key, value in data.__dict__.items():
            if not key.startswith('_'):
                globals()[key] = value
    except ImportError:
        pass

# Remove start markers
for combine in COMBINE_MEDIA:
    if '!START!' not in COMBINE_MEDIA[combine]:
        continue
    index = list(COMBINE_MEDIA[combine]).index('!START!')
    COMBINE_MEDIA[combine] = COMBINE_MEDIA[combine][:index] + \
        COMBINE_MEDIA[combine][index+1:]

try:
    from settings_overrides import *
except ImportError:
    pass
