# -*- coding: latin-1 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from ragendja.template import render_to_response
from django import forms
from django.conf import settings
from django.template import RequestContext

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login

from util.recaptcha.client import captcha
import logging

from django.contrib.auth.decorators import login_required
from ragendja.auth.decorators import staff_only
from ragendja.dbutils import transaction

from ts.search.models import TallstreetUrls, TallstreetUniverse, TallstreetTags
from ts.traders.models import TallstreetPortfolio, TallstreetTransaction, Log
from google.appengine.ext import db

from google.appengine.api.urlfetch import fetch
import re
from util.BeautifulSoup import BeautifulSoup

import urlparse


from connect.FacebookConnectMiddleware import FacebookConnectMiddleware
from connect.pyfacebook import Facebook

class UserField(forms.CharField):
	def clean(self, value):
		super(UserField, self).clean(value)
		user = User.get_by_key_name("user%s" % value)
		if user:
			raise forms.ValidationError("Someone is already using this username. Please pick an other.")
		else:
			return value

class RegisterForm(forms.Form):
	username = UserField(max_length=30)
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput())
	password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat your password")

	def clean_password(self):
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError('Passwords are not the same')
		return self.data['password']

	def clean(self,*args, **kwargs):
		self.clean_password()
		return super(RegisterForm, self).clean(*args, **kwargs)
	
class EditDetailsForm(forms.Form):
	email = forms.EmailField()
	current_password = forms.CharField(widget=forms.PasswordInput(), required=False)
	password = forms.CharField(widget=forms.PasswordInput(), required=False)
	password2 = forms.CharField(widget=forms.PasswordInput(), label="Repeat your password", required=False)

	def clean_password(self):
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError('Passwords are not the same')
		return self.data['password']

	def clean(self,*args, **kwargs):
		self.clean_password()
		return super(EditDetailsForm, self).clean(*args, **kwargs)	


def render(template, payload, request):
	if request.facebook_message is not None:
		facebook_message = request.facebook_message
	else:
		facebook_message = ''
	return render_to_response(request, template, payload)

def register(request, page):
	payload = {}
	if request.method == 'POST': 
		f = RegisterForm(request.POST) 
		if request.POST.has_key('toc'):
			if f.is_valid(): 
				check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
				if check_captcha.is_valid:
					user = User(key_name="user%s" % f.data['username'], username=f.data['username'], email=f.data['email'])
					user.set_password(f.data['password'])
					user.is_active = True
					user.put()
					#automatically login
					user = authenticate(username=f.data['username'],password=f.data['password'])
					if user is not None:
						if user.is_active:
							login(request, user)
					if request.session.test_cookie_worked():
						request.session.delete_test_cookie()	
					if request.GET.has_key("next"):	
						return HttpResponseRedirect(request.GET["next"]) 
					else:					
						return HttpResponseRedirect('/account/') 
				else:
					payload["captchaerror"] = True
		else:
			payload["tocerror"] = True
	else:
		f = RegisterForm()
	request.session.set_test_cookie()		
	payload["captchahtml"] = captcha.displayhtml(settings.RECAPTCHA_PUB_KEY)
	payload["form"] = f
	if request.GET.has_key("next"):
		payload["next"] = request.GET["next"]
	return render("register.html", payload, request)
	
def reset_password(request):
	payload = {}
	return render("accounthome.html", payload, request)

@login_required
def account(request):
	payload = {}
	return render("accounthome.html", payload, request)

@login_required
def transactions(request):
	payload = {}
	return render("transactions.html", payload, request)

@login_required
def portfolio(request, category):
	payload = {}
	return render("portfolio.html", payload, request)

@login_required
def invest(request, url, new_keyword = ""):
	if not(re.search("^http", url)):
		url = "http://%s" % url
	

	payload = {}
	keywords = []
	payload["base_balance"] = request.user.money_outstanding
	payload["this_investment"] = 0
	if request.method == 'POST': 	
		if request.POST.has_key("sitename"):
			dburl = TallstreetUrls.get_or_insert("url%s" % url)
			dburl.title = request.POST["sitename"]
			dburl.description = request.POST["description"]
			dburl.url = url
			dburl.put()
		else:
			dburl = TallstreetUrls.get_url(url)	
		i = 0
		while True:
			if not(request.POST.has_key("investment[%s]" % i)):
				break
			investment = request.POST["investment[%s]" % i]
			keyword = request.POST["keyword[%s]" % i]
			if not(request.POST.has_key("edit[%s]" % i)):
				edit = True
			else:
				edit = request.POST["edit[%s]" % i]
			keywords.append({"keyword": keyword, "amount": investment, 'edit': edit})
			investment = investment.replace(".", "")
			investment = investment.replace(",", "")
			investment = investment.replace("$", "")
			#investment = investment.replace("¢", "")
			if investment == "":
				investment = 0
			else:
				investment = int(investment)
			payload["base_balance"] -= investment
			payload["this_investment"] += investment
			keyword = keyword.replace("_", " ")
			keyword = keyword.strip()
			if keyword == "" and investment > 0:
				payload["error"] = "You must enter a keyword"
				payload["errorrow"] = i
			elif keyword == "" and investment == 0:
				pass
			elif investment < 0:
				payload["error"] = "You must invest a positive amount"
				payload["errorrow"] = i			
			else:
				try:
					update_url(request.user, keyword, dburl, investment, request.META["REMOTE_ADDR"])
				except forms.ValidationError, error:
					payload["error"] = error.messages[0]
					payload["errorrow"] = i
			i += 1
		if not(payload.has_key("error")):
			return HttpResponseRedirect('/portfolio') 
			
	payload["tags"] = {}
	dburl = TallstreetUrls.get_url(url)	

	if not(dburl):
		dburl = TallstreetUrls.get_url(url[0:-1])	
		if dburl:
			url = url[0:-1]
	if dburl:
		payload["url"] = dburl.url
		payload["title"] = dburl.title 
		payload["description"] = dburl.description
		payload["new"] = False
			
		for keyword in dburl.related_keywords:
			payload["tags"][keyword.tag.tag] = min(keyword.money / 1000 + 10, 30)
	else:
		page = fetch(url)
		soup = BeautifulSoup(page.content)
		payload["title"] = soup.html.head.title.string
		desc = soup.find("meta", {"name": "description"})
		if desc:
			payload["description"] = desc["content"]
		payload["url"] = url
		payload["new"] = True
		
	
	if keywords == []:
		invested = TallstreetPortfolio.get_keywords(request.user, dburl)
		for keyword in invested:
			if payload["tags"].has_key(keyword.keyword.tag):
				del payload["tags"][keyword.keyword.tag]	
			if keyword.keyword.tag == new_keyword:
				new_keyword = ""
			keywords.append({"keyword": keyword.keyword.tag, "amount": keyword.money, 'edit': False})
			payload["base_balance"] -= keyword.money
			payload["this_investment"] += keyword.money
		if payload["tags"].has_key(new_keyword):
			del payload["tags"][new_keyword]			
		keywords.append({"keyword": new_keyword, "amount": "0", 'edit': True})
	payload["keywords"] = keywords
	
	return render("invest.html", payload, request)
	
def update_url(user, keyword, url, investment, ip):
	tag = TallstreetTags.getKeyName(keyword)
	dbkeyword = TallstreetTags.get_or_insert(tag)
	if not(dbkeyword.tag):
		dbkeyword.tag = keyword
		dbkeyword.count = 1
	else:
		dbkeyword.count += 1			
	change = update_portfolio(user, dbkeyword, url, investment, ip)
	if change == 0:
		return
	
	dbuniverse = TallstreetUniverse.get_universe(dbkeyword, url)
				
	if dbuniverse:
		dbuniverse.money += change
	else:
		dbuniverse = TallstreetUniverse.get_or_insert("universe%s%s" % (dbkeyword.key(), url.key()))
		dbuniverse.money = change
		dbuniverse.tag = dbkeyword
		dbuniverse.url = url

	if dbuniverse.money == 0:
		dbuniverse.delete()
		dbkeyword.count -= 1	
	else:		
		dbuniverse.put()
	dbkeyword.put()
	
@transaction
def update_portfolio(user, keyword, url, investment, ip):
	portfolio = TallstreetPortfolio.get_invested(user, url, keyword)
	if not(portfolio):
		portfolio = TallstreetPortfolio(parent=user, key_name='url%skeyword%s' % (url.key(), keyword.key()))
		portfolio.url = url
		portfolio.keyword = keyword
		portfolio.user = user
		portfolio.money = investment
		if investment == 0:
			return 0
		change = investment
	else:
		change = investment - portfolio.money
		if change == 0:
			return 0
		portfolio.money = investment
	if user.money_outstanding - change < 0:
		raise forms.ValidationError("No Money left in account.")
	
	user.money_outstanding -= change
	if investment == 0:
		portfolio.delete()
		portfolio = None
	else:
		portfolio.put()
	transaction = TallstreetTransaction(parent=user, change=change, new_amount=investment, account_balance=user.money, account_balance_outstanding=user.money_outstanding, portfolio=portfolio, user=user, ip=ip)
	if change > 0:
		transaction.description = "Bought in [%s] under %s" % (url.key().id_or_name(), keyword.tag)
	else:
		transaction.description = "Sold in [%s] under %s" % (url.key().id_or_name(), keyword.tag)
	transaction.put()
	
	user.put()
	return change
	
	
@transaction
def update_portfolio_gain(user, url, keyword, gain):
	portfolio = TallstreetPortfolio.get_invested(user, url, keyword)
	change = long(round(portfolio.money * (1.0 * gain / 100)))

	if change == 0:
		return 0	
	portfolio.money = portfolio.money + change
		
	user.money += change
	if portfolio.money <= 0:
		portfolio.delete()
		portfolio = None
	else:
		portfolio.put()
	transaction = TallstreetTransaction(parent=user, change=change, new_amount=portfolio.money, account_balance=user.money, account_balance_outstanding=user.money_outstanding, portfolio=portfolio, user=user)
	if change > 0:
		transaction.description = "Gained in [%s] under %s" % (url.key().id_or_name(), keyword.tag)
	else:
		transaction.description = "Lost in [%s] under %s" % (url.key().id_or_name(), keyword.tag)
	transaction.put()
	
	user.put()
	return change	
	
@transaction
def update_new_money(user):
	if user.money_outstanding < 1000:
		user.money += 100
		user.money_outstanding += 100
	
	user.put()

def invest_url(request):
	payload = {}
	if request.GET.has_key('url'):
		url = request.GET['url']
		return HttpResponseRedirect('/invest/' + request.GET['url']) 
	
	if request.META.has_key("HTTP_REFERER"):
		payload = {}
		payload["referrer"] = get_referrer(request)
		if payload["referrer"]:
			return render("investrefer.html", payload, request)
	
	if request.user.is_authenticated():
		return render("investurl.html", payload, request)
	else:
		return redirect_to_login("/invest")

@login_required
def invest_add_url(request, keyword):
	return invest(request, request.GET['url'], keyword)

def index(request):
	payload = {}
	if request.META.has_key("HTTP_REFERER"):
		payload = {}
		payload["referrer"] = get_referrer(request)
	return render('index.html', payload, request)
		
def get_referrer(request):
	parsed = urlparse.urlparse(request.META["HTTP_REFERER"])
	if parsed[1].find(request.META["SERVER_NAME"]) == -1:
		url = TallstreetUrls.get_url(request.META["HTTP_REFERER"])
		if not(url):
			domain = urlparse.urlunparse((parsed[0], parsed[1], '', '', '', ''))
			url = TallstreetUrls.get_url(domain)	
		return url
	return False	

@login_required
def editdetails(request):
	payload = {}
	if request.method == 'POST': 
		f = EditDetailsForm(request.POST) 
		if f.is_valid():
			request.user.email = f.data['email']
			if f.data['current_password']:
				if request.user.check_password(f.data['current_password']):
					request.user.set_password(f.data['password'])
					request.user.save()
					return HttpResponseRedirect('/account/') 
				else:
					payload['incorrectpassword'] = True
			else:
				request.user.save()
				return HttpResponseRedirect('/account/') 
	else:
		f = EditDetailsForm(initial={'email': request.user.email})
	payload["form"] = f	
	return render("editdetails.html", payload, request)

@login_required		
def logout_view(request):
	logout(request)			
	FacebookConnectMiddleware.delete_fb_cookies = True
	return HttpResponseRedirect('/') 
	
@staff_only
def send_connect_users(request):
	payload = {}
	users = User.all().filter('email_hash = ', None).fetch(100)
	hashes = []
	fb = Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_API_SECRET)
	for user in users:
		#logging.debug(user)
		user.email_hash = fb.hash_email(user.email)
		hashes.append({"email_hash": user.email_hash})
		user.put()
	user_info_response = fb.connect.registerUsers(hashes)
	return render("standardpage.html", payload, request)


def connect_users(request):
	#<QueryDict: {u'fb_sig_time': [u'1230351016.3299'], 
	#			u'fb_sig_authorize': [u'1'], 
	#			u'fb_sig_locale': [u'en_US'], 
	#			u'fb_sig_session_key': [u'2.oYf3yaL9PnROgLyp5cBg9A__.86400.1230440400-1144902201'], 
	#			u'fb_sig_in_new_facebook': [u'1'], 
	#			u'fb_sig_profile_update_time': [u'0'], 
	#			u'fb_sig_user': [u'1144902201'], 
	#			u'fb_sig_expires': [u'1230440400'], 
	#			u'fb_sig': [u'807f94cba0b3a26f359cd5a7c16cdcd6'], 
	#			u'fb_sig_api_key': [u'9669d802ca3cdcc15172ccd7b4636646'], 
	#			u'fb_sig_added': [u'1']}>
	payload = {}
	logging.info(request.POST)
	fb = Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_API_SECRET)
	fb.session_key = request.POST['fb_sig_session_key']
	user_info_response = fb.users.getInfo([request.POST['fb_sig_user']], ['email_hashes', 'first_name', 'last_name'])
	logging.info(user_info_response)
	for hash in user_info_response[0]['email_hashes']:
		user = User.all().filter('email_hash = ', hash).get()
		user.facebook_id = int(request.POST['fb_sig_user'])
		user.put()
	return render("standardpage.html", payload, request)