from django.contrib.auth.models import User
import logging

class FacebookBackend:
	"""
	Authenticate against facebook
	"""
	def authenticate(self, facebook_id=None):
		if facebook_id == None:
			return None
		user = User.all().filter('facebook_id = ', int(facebook_id)).get()
		return user

	def get_user(self, user_id):
		return User.get(user_id)