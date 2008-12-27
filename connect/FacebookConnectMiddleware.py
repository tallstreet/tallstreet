# FacebookConnectMiddleware.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings

import md5
import urllib
import time
from django.utils import simplejson
from datetime import datetime
import logging 
from connect.pyfacebook import Facebook

# These values could be placed in Django's project settings
API_KEY = settings.FACEBOOK_API_KEY
API_SECRET = settings.FACEBOOK_API_SECRET

PROBLEM_ERROR = 'There was a problem. Try again later.'
ACCOUNT_DISABLED_ERROR = 'Your account is not active.'
ACCOUNT_PROBLEM_ERROR = 'There is a problem with your account.'

class FacebookConnectMiddleware(object):
	
	delete_fb_cookies = False
	facebook_user_is_authenticated = False
	
	def process_request(self, request):
		try:
			 # Set the facebook message to empty. This message can be used to dispaly info from the middleware on a Web page.
			request.facebook_message = None
	
			# Don't bother trying FB Connect login if the user is already logged in
			if not request.user.is_authenticated():
				# FB Connect will set a cookie with a key == FB App API Key if the user has been authenticated
				if API_KEY in request.COOKIES:
					fb = Facebook(API_KEY, API_SECRET)

					if(fb.validate_cookie_signature(request.COOKIES)):
				
						# If session hasn't expired
						if(datetime.fromtimestamp(float(request.COOKIES[API_KEY+'_expires'])) > datetime.now()):
			
							# Try to get Django account corresponding to friend
							# Authenticate then login (or display disabled error message)
							user = authenticate(facebook_id=request.COOKIES[API_KEY + '_user'])
							logging.info(user)
							if user is not None:
								if user.is_active:
									login(request, user)
									self.facebook_user_is_authenticated = True
								else:
									request.facebook_message = ACCOUNT_DISABLED_ERROR
									self.delete_fb_cookies = True
							else:
								django_user = User.get_by_key_name("userfb%s" % request.COOKIES[API_KEY + '_user'])
								if not django_user:
									# There is no Django account for this Facebook user.
									# Create one, then log the user in.
									fb.session_key = request.COOKIES[API_KEY + '_session_key']
									user_info_response = fb.users.getInfo([request.COOKIES[API_KEY + '_user']], ['first_name', 'last_name'])
							
									# Create user
									user = User(key_name="userfb%s" % request.COOKIES[API_KEY + '_user'], username = "%s %s" % (user_info_response[0]['first_name'], user_info_response[0]['last_name']), 
												email= '%s@connect.facebook.com' % request.COOKIES[API_KEY + '_user'])
									user.set_password(md5.new(request.COOKIES[API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
									user.is_active = True
									user.facebook_id = int(request.COOKIES[API_KEY + '_user'])
									user.put()
							
									# Authenticate and log in (or display disabled error message)
									user = authenticate(username='%s@connect.facebook.com' % request.COOKIES[API_KEY + '_user'], 
											password=md5.new(request.COOKIES[API_KEY + '_user'] + settings.SECRET_KEY).hexdigest())
									logging.info("ROUND2")
									if user is not None:
										if user.is_active:
											login(request, user)
											self.facebook_user_is_authenticated = True
										else:
											request.facebook_message = ACCOUNT_DISABLED_ERROR
											self.delete_fb_cookies = True
									else:
										request.facebook_message = ACCOUNT_PROBLEM_ERROR
										self.delete_fb_cookies = True
								else:								
									request.facebook_message = ACCOUNT_PROBLEM_ERROR
									self.delete_fb_cookies = True
								
						# Cookie session expired
						else:
							logout(request)
							self.delete_fb_cookies = True
						
				   # Cookie values don't match hash
					else:
						logout(request)
						self.delete_fb_cookies = True
					
			# Logged in
			else:
				# If FB Connect user
				if API_KEY in request.COOKIES:
					# IP hash cookie set
					if 'fb_ip' in request.COOKIES:
					
						try:
							real_ip = request.META['HTTP_X_FORWARDED_FOR']
						except KeyError:
							real_ip = request.META['REMOTE_ADDR']
					
						# If IP hash cookie is NOT correct
						if request.COOKIES['fb_ip'] != md5.new(real_ip + API_SECRET + settings.SECRET_KEY).hexdigest():
							 logout(request)
							 self.delete_fb_cookies = True
					# FB Connect user without hash cookie set
					else:
						logout(request)
						self.delete_fb_cookies = True
				
		# Something else happened. Make sure user doesn't have site access until problem is fixed.
		except:
			request.facebook_message = PROBLEM_ERROR
			logout(request)
			self.delete_fb_cookies = True
	
	def process_response(self, request, response):
		# Delete FB Connect cookies
		# FB Connect JavaScript may add them back, but this will ensure they're deleted if they should be
		if self.delete_fb_cookies is True:
			response.delete_cookie(API_KEY + '_user')
			response.delete_cookie(API_KEY + '_session_key')
			response.delete_cookie(API_KEY + '_expires')
			response.delete_cookie(API_KEY + '_ss')
			response.delete_cookie(API_KEY)
			response.delete_cookie('fbsetting_' + API_KEY)
		
		self.delete_fb_cookies = False
		
		if self.facebook_user_is_authenticated is True:
			try:
				real_ip = request.META['HTTP_X_FORWARDED_FOR']
			except KeyError:
				real_ip = request.META['REMOTE_ADDR']
				response.set_cookie('fb_ip', md5.new(real_ip + API_SECRET + settings.SECRET_KEY).hexdigest())
			
		# process_response() must always return a HttpResponse
		return response
				
