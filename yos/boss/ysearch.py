# Copyright (c) 2008 Yahoo! Inc. All rights reserved.
# Licensed under the Yahoo! Search BOSS Terms of Use
# (http://info.yahoo.com/legal/us/yahoo/search/bosstos/bosstos-2317.html)

"""
This is the Boss search API
search is the main function

Examples:
  web_results = search("britney spears")
  news_20_results = search("tiger woods", vertical="news", count=20)
"""

__author__ = "Vik Singh (viksi@yahoo-inc.com)"

import types
import urllib
import datetime

from django.utils import simplejson
from yos.crawl import rest
from yos.crawl import xml2dict
from google.appengine.api import memcache

CONFIG = {"appid": "V1IoiCfV34Hb7uyGlM4dbNGnrlxjj0uP91_TA6uKSgGNki4kf5A244zyZWaYyQc01.c-",
 "email": "garfunckle1@yahoo.com",
 "org": "",
 "agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0",
 "commercial": False,
 "purpose": "Demonstrate the power of Y! Search BOSS",
 "version": "1.0",
 "uri": "http://boss.yahooapis.com/ysearch/"
}

SEARCH_API_URL = CONFIG["uri"].rstrip("/") + "/%s/v%d/%s?start=%d&count=%d&lang=%s&region=%s&filter=%s" + "&appid=" + CONFIG["appid"]
SUGGEST_API_URL = "http://search.yahooapis.com/WebSearchService/V1/relatedSuggestion?output=json&query=%s&appid=" + CONFIG["appid"]
GLUE_API_URL = glueurl = "http://glue.yahoo.com/template/index.php?query=%s"

def params(d):
  """ Takes a dictionary of key, value pairs and generates a cgi parameter/argument string """
  p = ""
  for k, v in d.iteritems():
    p += "&%s=%s" % (iri_to_uri(k), iri_to_uri(v))
  return p

def search(command, vertical="web", version=1, start=0, count=10, lang="en", region="us", filter="-porn-hate", more={}):
  """
  command is the query (not escaped)
  vertical can be web, news, spelling, images
  lang/region default to en/us - take a look at the the YDN Boss documentation for the supported lang/region values
  """
  url = SEARCH_API_URL % (vertical, version, iri_to_uri(command), start, count, lang, region, filter) + params(more)
  data = load(url)
  if data:
	return simplejson.loads(data)

def suggest(query):
	url = SUGGEST_API_URL % iri_to_uri(query)
	data = load(url)
	if data:
		return simplejson.loads(data)

def glue(query):
	url = GLUE_API_URL % iri_to_uri(query)
	data = load(url)
	if data:
		return xml2dict.fromstring(data)

def load(url):
    data = memcache.get(url)
    if data is not None:
      return data
    data = rest.download(url)
    if data:
      memcache.set(url, data, 3600)
      return data

def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def iri_to_uri(iri):
    """
    Convert an Internationalized Resource Identifier (IRI) portion to a URI
    portion that is suitable for inclusion in a URL.

    This is the algorithm from section 3.1 of RFC 3987.  However, since we are
    assuming input is either UTF-8 or unicode already, we can simplify things a
    little from the full method.

    Returns an ASCII string containing the encoded result.
    """
    # The list of safe characters here is constructed from the printable ASCII
    # characters that are not explicitly excluded by the list at the end of
    # section 3.1 of RFC 3987.
    if iri is None:
        return iri
    return urllib.quote(smart_str(iri), safe='/#%[]=:;$&()+,!?*')

