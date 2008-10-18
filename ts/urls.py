from django.conf.urls.defaults import *
from ts.search.feeds import ResultsFeed, HistoryCalcFeed, PortfolioCalcFeed

feeds = {
    'results': ResultsFeed,
    'calchistory': HistoryCalcFeed,
    'calcportfolio': PortfolioCalcFeed
}


urlpatterns = patterns('',
    (r'^$', 'ts.traders.views.index'),
    (r'^(introduction.html)$', 'ts.views.htmlpage'),
    (r'^(privacy.html)$', 'ts.views.htmlpage'),
    (r'^(terms.html)$', 'ts.views.htmlpage'),
    (r'^(contactus.html)$', 'ts.views.htmlpage'),
    (r'^(buildlink.html)$', 'ts.views.htmlpage'),
    (r'^(promote.html)$', 'ts.views.htmlpage'),
    (r'^login.html$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^passwordforgotten.html$', 'django.contrib.auth.views.password_reset', {'template_name': 'passwordforgotten.html'}),
    (r'^passwordresetdone.html$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'login.html'}),
		    
    (r'^(.*).php$', 'ts.views.redirect'),
    (r'^view/(.*)/$', 'ts.search.views.view'),
    (r'^view/(.*)/page([0-9]+)$', 'ts.search.views.view'),
    (r'^search.do$', 'ts.search.views.search'),		  
    (r'^click.do$', 'ts.search.views.click'),		   
    (r'^rating.do$', 'ts.search.views.rating'),   
    (r'^url/(.*)$', 'ts.search.views.url'),				       
		    
    (r'^account/', include('ts.traders.urls')),
    (r'^invest/?$', 'ts.traders.views.invest_url'),
    (r'^invest/(.+)$', 'ts.traders.views.invest'),
    (r'^add/(.+)/?$', 'ts.traders.views.invest_add_url'),
    (r'^portfolio/?(.*)$', 'ts.traders.views.portfolio'),
		    
    (r'^(register.html)$', 'ts.traders.views.register'),
    (r'^(register.do)$', 'ts.traders.views.register'),
		    
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
		    
    #(?P<username>[^\.^/]+)
    )
