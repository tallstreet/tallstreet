from django.conf.urls.defaults import *

urlpatterns = patterns('ts.traders.views',
    (r'^logout.html$', 'logout_view'),
    (r'^transactions.html$', 'transactions'),
    (r'^editdetails.html$', 'editdetails'),
    (r'^click$', 'dequeuerating'),
    (r'^rating$', 'dequeuerating'),
    (r'^calchistory$', 'dequeuehistory'),
    (r'^updatenewmoney$', 'cronupdate_new_money'),
    (r'^$', 'account')
    )
