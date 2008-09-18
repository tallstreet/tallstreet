from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from ragendja.template import render_to_response
from django.template import RequestContext
from google.appengine.ext import db

def render(template, payload, request):
    return render_to_response(request, template, payload)


def htmlpage(request, page):
    payload = {}
    payload['user'] = request.user
    return render(page, payload, request)

def redirect(request, page):
    return HttpResponsePermanentRedirect(page + '.html')

