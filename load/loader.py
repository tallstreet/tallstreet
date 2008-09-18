import os, sys

import logging
# Add folder to sys.path, so we can import aecmd
sys.path = [os.path.abspath(os.path.dirname(__file__) + "/../common/appenginepatch/"),] + sys.path

from aecmd import setup_project
setup_project()

from appenginepatcher.patch import patch_all, setup_logging
patch_all()

import bulkload
from google.appengine.api import datastore_types
from google.appengine.ext import search
from google.appengine.api import datastore
from google.appengine.ext import db

import datetime

from ts.search.models import TallstreetUrls, TallstreetTags, TallstreetUniverse, TallstreetHistory
from ts.traders.models import TallstreetPortfolio


from django.contrib.auth.models import User


class URLLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'TallstreetUrls',
                         [('url', datastore_types.Link),
			  ('title', datastore_types.Text),
			  ('description', datastore_types.Text)
                          ])

  def HandleEntity(self, entity):
	url = TallstreetUrls()
	url.url = entity["url"]
	url.title = entity["title"]
	if entity.has_key("description"):
		url.description = entity["description"]
	else:
		url.description = ""
	newent = datastore.Entity('TallstreetUrls', name="url%s" % (entity['url']))	
	url._to_entity(newent)	
	return newent
    
class TagLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'TallstreetTags',
                         [('stemmedtag', datastore_types.Category),
			  ('tag', datastore_types.Category),
			  ('count', int)
                          ])

  def HandleEntity(self, entity):
    newent = datastore.Entity('TallstreetTags',name="tag" + entity['stemmedtag'])
    del entity['stemmedtag']
    newent.update(entity) 
    return newent    
  
class UniverseLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'TallstreetUniverse',
                         [('tag', datastore_types.Category),
			  ('url', str),
			  ('money', int)
                          ])

  def HandleEntity(self, entity):
	url = datastore_types.Key.from_path("TallstreetUrls", 'url' + entity['url'])
	keyword = datastore_types.Key.from_path("TallstreetTags", 'tag' + entity['tag'])	  
	universe = TallstreetUniverse(key_name="universe%s%s" % (keyword, url))
	universe.money = entity["money"]
	universe.tag = keyword
	universe.url = url
	newent = datastore.Entity('TallstreetUniverse', name="universe%s%s" % (keyword, url))	
	universe._to_entity(newent)
	return newent
  

class HistoryLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'TallstreetHistory',
                         [('url', str),
			  ('tag', datastore_types.Category),
			  ('date', str),
			  ('change', long)
                          ])

  def HandleEntity(self, entity):
	if not entity['tag']:
		return []
	url = datastore_types.Key.from_path("TallstreetUrls", 'url' + entity['url'])
	keyword = datastore_types.Key.from_path("TallstreetTags", 'tag' + entity['tag'])
	history = TallstreetHistory.get_or_insert(key_name="history%s%s" % (keyword, url))
	universe = datastore_types.Key.from_path("TallstreetUniverse", "universe%s%s" % (keyword, url))	  
	history.universe = universe
	history.changes.insert(0, entity['change'])
	history.dates.insert(0, datetime.datetime.strptime(entity['date'], "%Y-%m-%d %H:%M:%S"))
	history.put()
	return []
  

class UsersLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'User',
                         [('username', str),
			  ('date_joined', str),
			  ('email', datastore_types.Email),
			  ('last_login', str),
			  ('money', long),
			  ('money_outstanding', long),
			  ('password', str)
                          ])

  def HandleEntity(self, entity):
	user = datastore.Entity('User', name="user" + entity['username'])	
	user["date_joined"]  = datetime.datetime.strptime(entity['date_joined'], "%Y-%m-%d %H:%M:%S")
	user["email"]  = entity['email']
	user["is_active"]  = True
	user["is_banned"]  = False
	user["is_staff"]  = False
	user["is_superuser"] = True
	user["last_login"]   = datetime.datetime.strptime(entity['last_login'], "%Y-%m-%d %H:%M:%S")
	user["modified"]   = datetime.datetime.now()
	user["money"]  = entity['money']
	user["money_outstanding"]  = entity['money_outstanding']
	user["password"]  = "md5$$" + entity['password']
	user["username"]  = entity['username']
	return user
  

class PortfolioLoader(bulkload.Loader):
  def __init__(self):
    bulkload.Loader.__init__(self, 'TallstreetPortfolio',
                         [('username', str),
                          ('url', datastore_types.Link),
			  ('tag', datastore_types.Category),
			  ('money', long)
                          ])

  def HandleEntity(self, entity):
	url = datastore_types.Key.from_path("TallstreetUrls", 'url' + entity['url'])
	keyword = datastore_types.Key.from_path("TallstreetTags", 'tag' + entity['tag'])	
	user = datastore_types.Key.from_path("User", "user" + entity['username'])	
	portfolio = TallstreetPortfolio(key_name='url%skeyword%s' % (url, keyword))
	portfolio.user  = user
	portfolio.url  = url
	portfolio.user  = user
	portfolio.keyword  = keyword
	portfolio.money  = entity['money']

	newent = datastore.Entity('TallstreetPortfolio', name='url%skeyword%s' % (url, keyword), parent=user)
	portfolio._to_entity(newent)	
	return newent  
    
if __name__ == '__main__':
  bulkload.main(URLLoader(), TagLoader(), UniverseLoader(), HistoryLoader(), UsersLoader(), PortfolioLoader())
