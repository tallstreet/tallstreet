from google.appengine.ext import db
from django import forms

from ragendja.auth.models import EmailUser

from string import ascii_letters, digits
import hashlib, random
import logging

def gen_hash(password, salt=None, algorithm='sha512'):
	hash = hashlib.new(algorithm)
	hash.update(password)
	if salt == None:
		salt = ''.join([random.choice(ascii_letters + digits) for _ in range(8)])
	hash.update(salt)
	return (algorithm, salt, hash.hexdigest())

class User(EmailUser):
	money = db.IntegerProperty(default=50)
	money_outstanding = db.IntegerProperty(default=50)
	username = db.StringProperty(required=True)
	
	
	def check_password(self, password):
		if not self.has_usable_password():
			return False
		algorithm, salt, hash = self.password.split('$')
		return hash == gen_hash(password, salt, algorithm)[2]	