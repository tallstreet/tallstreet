from django.contrib.syndication.feeds import FeedDoesNotExist
from django.contrib.syndication.feeds import Feed

from ts.search.views import get_local_results
from ts.search.models import TallstreetUniverse, TallstreetClick, TallstreetUrls, TallstreetTags

import logging


class ResultsFeed(Feed):
    def get_object(self, category):
	category = category[0].replace("_", " ")
	tagdata = TallstreetTags.get(category)
	if not tagdata:
            raise FeedDoesNotExist
        return tagdata

    def title(self, obj):
        return "Results under %s" % obj.tag

    def link(self, obj):
        return '/view/' + obj.tag.replace(" ", "_") + '/'

    def description(self, obj):
        return "Results under %s" % obj.tag
    
    
    def item_link(self, item):
        return item.url.url

    def items(self, obj):
	return get_local_results(0, 10, obj, None)
