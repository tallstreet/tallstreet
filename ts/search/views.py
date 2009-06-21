from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponseNotFound
from ragendja.template import render_to_response
from ts.search.models import TallstreetUniverse, TallstreetUrls, TallstreetTags
from ts.traders.models import TallstreetPortfolio

from yos.boss.ysearch import search as ysearch
from yos.boss.ysearch import suggest
from yos.boss.ysearch import glue
from yos.crawl.rest import load_json
from yos.crawl.rest import load_xml

import logging

import tags
from django.http import HttpRequest, QueryDict
from django.core.cache import cache
from django.utils.http import urlquote
from google.appengine.api.labs.taskqueue import Task


def render(request, template, payload):
	return render_to_response(request, template, payload)

def view(request, category, page = 1):
	category = category.replace("_", " ")
	tagdata = TallstreetTags.get(category)
	payload = {}
	size = 10
	page = int(page)
	
	payload["page"] = page
	payload["size"] = size
	payload["search"] = category
	payload["results2"] = []
    

	if tagdata and tagdata.count > 30:
		payload["hits"] = tagdata.count
		payload["results"] = get_local_results(int((page - 1) * size), size, tagdata, request.user)
	elif tagdata:
		offset = int((page - 1) * size)
		if offset < tagdata.count and offset + size <= tagdata.count:
			# just a random number of hits (not worth querying yahoo to get exact number)
			payload["hits"] = tagdata.count + 19223211
			payload["results"] = get_local_results(offset, size, tagdata, request.user)
		elif offset < tagdata.count and offset + size > tagdata.count:
			localresults = tagdata.count - offset
			payload["results"] = get_local_results(offset, localresults, tagdata, request.user)
			(hits, results) = get_boss_results(0, size - localresults, category)
			payload["hits"] = tagdata.count + hits
			payload["results2"] = results
		else:
			(hits, payload["results"]) = get_boss_results(offset - tagdata.count, size, category)
			payload["hits"] = tagdata.count + hits
	else:
		(payload["hits"], payload["results"]) = get_boss_results(int((page - 1) * size), size, category)

	payload["results_per_page"] = size
	payload["last_on_page"] = page * size
	payload["page"] = page
	if payload["hits"] > size:
		payload["pages"] = ((payload["hits"] - size) / payload["results_per_page"]) + 2
	else:
		payload["pages"] = 1
	payload["next"] = page + 1
	payload["previous"] = page - 1
	payload["has_next"] = page < payload["pages"]
	payload["has_previous"] = page > 1
	payload["paginator_param"] = "/view/%s/" % category.replace(" ", "_")
	payload["search_text"] =  "<a href='%s'>%s</a> - Displaying %s to %s of %s" % (payload["paginator_param"], category, payload["last_on_page"] - size + 1, payload["last_on_page"], payload["hits"])
	return render(request, 'results.html', payload)
	
def get_local_results(offset, size, category, user):
	localresult = TallstreetUniverse.get_results(offset, size, category)
	results = []
	for result in localresult:
		result.urlkey = result._url.id_or_name()
		try:
			if not cache.get("url:" + urlquote(result._url.id_or_name())):
				url = result.url
		except:
			logging.error("No url" )
			continue
		i = 0	
		related_keywords_display = []
		for related_keywords in result.url.related_keywords:
			if i > 5:
				break
			i += 1
			related_keywords_display.append(related_keywords)
			
		result.url.related_keywords_display = related_keywords_display
		if user and user.is_authenticated():
			portfolio = TallstreetPortfolio.get_invested(user, result._url, category)
			if portfolio:
				result.money_invested = portfolio.money
		results.append(result)
	
	return results
		
def get_boss_results(offset, size, category):
	result = ysearch(category, count=size, start=offset)
	
	ysr = result['ysearchresponse']
	
	results = []
	if ysr.has_key('resultset_web'):
		i = 0
		for result in ysr['resultset_web']:
			i += 1
			money  = 1100 - offset * 10 - i * 10
			if money < 20:
				money = 20
			result['description'] = result['abstract']
			result['url'] = result['url'].replace("&amp;", "&")
			results.append({'boss': True, 'money': money, 'url': result})
	
	hits = int(ysr['totalhits'])		
	return (hits, results)

def search(request):
	result = TallstreetTags.get(request.GET['query'])
	if result:
		return HttpResponsePermanentRedirect('/view/' + result.tag.replace(" ", "_") + '/')
	else:
		return HttpResponsePermanentRedirect('/view/' + request.GET['query'].replace(" ", "_") + '/')
	
def click(request):
	t = Task(url='/queue/click', params={'keyword': request.POST["keywords"], 'url': request.POST["url_id"],'ip': request.META["REMOTE_ADDR"]})
	t.add('processratings')
	return HttpResponse("", mimetype="text/plain")
	
def rating(request):
	t = Task(url='/queue/rating', params={'keyword': request.POST["keywords"], 'rating': int(request.POST["rating"]), 'url': request.POST["url_id"],'ip': request.META["REMOTE_ADDR"]})
	t.add('processratings')
	return HttpResponse("Thanks for rating", mimetype="text/plain")

def url(request, url):
	payload = {}
	payload["url"] = TallstreetUrls.get_url(url)
	if not payload["url"]:
		return HttpResponseNotFound('<h1>Url not added</h1><p>Click <a href="http://www.tallstreet.com/invest/%s">http://www.tallstreet.com/invest/%s</a> to add it.' % (url, url)) 
	payload["otherurls"] = payload["url"].get_other_urls()		
	return render(request, 'url.html', payload)

	    