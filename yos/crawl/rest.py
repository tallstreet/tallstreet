# Copyright (c) 2008 Yahoo! Inc. All rights reserved.
# Licensed under the Yahoo! Search BOSS Terms of Use
# (http://info.yahoo.com/legal/us/yahoo/search/bosstos/bosstos-2317.html)

""" Functions for downloading REST API's and converting their responses into dictionaries """

__author__ = "Vik Singh (viksi@yahoo-inc.com)"

import logging
import xml2dict

from django.utils import simplejson
from google.appengine.api import urlfetch
import logging

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0"}

def download(url):
	result = urlfetch.fetch(url, headers  = HEADERS)
	if result.status_code == 200:
		return result.content

def load_json(url):
  return simplejson.loads(download(url))

def load_xml(url):
  return xml2dict.fromstring(download(url))

def load(url):
  dl = download(url)
  try:
    return simplejson.loads(dl)
  except:
    return xml2dict.fromstring(dl)
