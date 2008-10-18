from google.appengine.ext import db
from django import forms

from ragendja.auth.models import EmailUser

from string import ascii_letters, digits
import hashlib, random
import logging

class User(EmailUser):
	money = db.IntegerProperty(default=50)
	money_outstanding = db.IntegerProperty(default=50)
	username = db.StringProperty(required=True)
	
	@classmethod
	def need_new_money(self):
		query = db.Query(User)
		query.filter('money_outstanding <', 1000)
		return query.fetch(500)	