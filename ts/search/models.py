from google.appengine.ext import db
from django import forms

import urlparse
import logging
import datetime

class TallstreetUrls(db.Expando):
	url = db.LinkProperty()   
	title = db.TextProperty()   
	description = db.TextProperty()   

	def get_other_urls(self):
		parsed = urlparse.urlparse(self.url)
		domain = urlparse.urlunparse((parsed[0], parsed[1], '', '', '', ''))
		query = db.Query(TallstreetUrls)
		query.filter('url >=', domain)
		query.filter('url <', domain + u"\xEF\xBF\xBD")
		otherurls = query.fetch(10)
		return 	otherurls
	
	@classmethod
	def get_url(self, url):
		return TallstreetUrls.get_by_key_name("url%s" % url)
  
class TallstreetTags(db.Model):
	tag = db.CategoryProperty()
	count = db.IntegerProperty()
	
	@classmethod
	def get(self, phrase):
		return db.get(self.getKey(phrase))
	
	@classmethod
	def getKey(self, phrase):
		return db.Key.from_path("TallstreetTags", self.getKeyName(phrase))
		
	@classmethod
	def getKeyName(self, phrase):
		return "tag" + phrase.lower()
  
	
class TallstreetUniverse(db.Model):
	tag = db.ReferenceProperty(TallstreetTags, collection_name='related_urls') 
	money = db.IntegerProperty()
	url = db.ReferenceProperty(TallstreetUrls, collection_name='related_keywords')
	
	@classmethod
	def get_universe(self, tag, url):
		query = db.Query(TallstreetUniverse)
		query.filter('url =', url)
		query.filter('tag =', tag)
		return query.get()
	
	
	@classmethod
	def get_results(self, offset, size, category):
		query = db.Query(TallstreetUniverse)
		query.filter('tag =', category)	
		query.order('-money')
		return query.fetch(size, offset=offset)	
	
class TallstreetHistory(db.Model):
	universe = db.ReferenceProperty(TallstreetUniverse, collection_name='history') 
	dates = db.ListProperty(datetime.datetime)
	changes = db.ListProperty(int)
	
class TallstreetHistoryChanges(db.Model):
	ips = db.ListProperty(str)	
	change = db.IntegerProperty(default=0)
	
	@classmethod
	def get_all(self):
		query = db.Query(TallstreetHistoryChanges)
		return query.fetch(100)
