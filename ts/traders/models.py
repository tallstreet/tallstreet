from google.appengine.ext import db
from django import forms
import logging

from django.contrib.auth.models import User
from ts.search.models import TallstreetUrls, TallstreetTags

	
class TallstreetPortfolio(db.Model):
	user = db.ReferenceProperty(User, collection_name='portfolio')
	url = db.ReferenceProperty(TallstreetUrls, collection_name='related_users')
	keyword = db.ReferenceProperty(TallstreetTags, collection_name='related_users')
	money = db.IntegerProperty()
	
	@classmethod
	def get_investors(self, url, tag):	
		query = db.Query(TallstreetPortfolio)
		query.filter('url =', url)
		query.filter('keyword =', tag)
		return query.fetch(1000)		

	@classmethod
	def get_invested(self, user, url, tag):	
		if isinstance(url, db.Key):
			urlkey = url
		else:
			urlkey = url.key()
		return TallstreetPortfolio.get_by_key_name('url%skeyword%s' % (urlkey, tag.key()), user)
	
	@classmethod
	def get_keywords(self, user, url):	
		query = db.Query(TallstreetPortfolio)
		query.ancestor(user)
		query.filter('url =', url)
		return query.fetch(50)	
	
class TallstreetTransaction(db.Model):
	user = db.ReferenceProperty(User, collection_name='transactions')
	portfolio = db.ReferenceProperty(TallstreetPortfolio, collection_name='transactions')
	change = db.IntegerProperty(required=True)	
	new_amount = db.IntegerProperty(required=True)	
	account_balance = db.IntegerProperty(required=True)	
	account_balance_outstanding = db.IntegerProperty(required=True)	
	time = db.DateTimeProperty(auto_now_add=True)	
	description = db.StringProperty()
	ip = db.StringProperty()
	
	@classmethod
	def get_transactions(self, user):	
		query = db.Query(TallstreetTransaction)
		query.ancestor(user)
		query.filter('url =', url)
		return query.fetch(50)	
		

class Log(db.Model):
	description = db.StringProperty()