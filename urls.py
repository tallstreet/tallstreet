# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'main.html'}),
    (r'^person/', include('myapp.urls')),
)
