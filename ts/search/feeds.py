from django.contrib.syndication.feeds import FeedDoesNotExist
from django.contrib.syndication.feeds import Feed

from ts.search.views import get_local_results
from ts.search.models import TallstreetUniverse, TallstreetClick, TallstreetUrls, TallstreetTags, TallstreetHistoryChanges, TallstreetHistory

from ts.traders.models import TallstreetPortfolio, TallstreetTransaction
from ts.traders.views import update_portfolio_gain, update_new_money
from django.contrib.auth.models import User
import logging
import datetime


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

class HistoryCalcFeed(Feed):
    title = "Tall Street Calculations"
    link = "/"
    description = "Calculate history feed"
    
    def item_link(self, item):
        return "/"

    def items(self, obj):
	ratings = []
	ips = []
	clicks =  TallstreetClick.get_all()
	history = False
	for click in clicks:
		click.delete()
		logging.debug("Analysing %s %s %s %s %s" % (click.url, click.keyword, click.ip, click.type, click.rating))
		url = TallstreetUrls.get_url(click.url)
		if not url:
			logging.debug("No url")
			continue
		
		keyword = TallstreetTags.get_by_key_name("tag%s" %click.keyword.lower())
		if not keyword:
			logging.debug("No keyword")
			continue
		
		universe = TallstreetUniverse.get_universe(keyword, url)	 
		if not universe:			
			logging.debug("No universe")
			continue 
		
		if ips == []:
			historychanges = TallstreetHistoryChanges.get_or_insert(key_name="history%s%s" % (keyword.key(), url.key()))
			ips = historychanges.ips		
		
		change = 0
		if click.type == 'C':
			change = 1
		elif click.type == 'R' and click.rating == 5:
			change = 50
		elif click.type == 'R' and click.rating == 4:
			change = 20
		elif click.type == 'R' and click.rating == 3:
			change = 10
		elif click.type == 'R' and click.rating == 2:
			change = 5
		elif click.type == 'R' and click.rating == 1:
			change = -20
			
		date = datetime.datetime(click.time.year, click.time.month, click.time.day)
		
		
		if click.ip + click.type in ips:
			continue
		ips.append(click.ip + click.type)
		
		if not history:
			history = TallstreetHistory.get_or_insert(key_name="history%s%s" % (keyword.key(), url.key()))
			history.universe = universe
			history.changes.insert(0, long(change))
			history.dates.insert(0, date)
		elif history.universe != universe or history.dates[0] != date:			
			logging.debug("Adding history %s %s %s" % (ips, history.changes[0], history.dates[0]))
			historychanges = TallstreetHistoryChanges.get_or_insert(history.key().id_or_name())
			historychanges.ips = ips
			historychanges.put()
			history.put()
			ips = []
			history = TallstreetHistory.get_or_insert(key_name="history%s%s" % (keyword.key(), url.key()))
			history.changes.insert(0, long(change))
			history.dates.insert(0, date)
			history.universe = universe
		else:					
			logging.debug("Add Change %s" % (change))
			history.changes[0] += long(change)
			
			
	
	if history:
		logging.debug("Adding history %s %s %s" % (ips, history.changes[0], history.dates[0]))
		historychanges = TallstreetHistoryChanges.get_or_insert(history.key().id_or_name())
		historychanges.ips = ips
		historychanges.put()
		history.put()	
	return []



class PortfolioCalcFeed(Feed):
    title = "Tall Street Calculations"
    link = "/"
    description = "Calculate traders feed"
    
    def item_link(self, item):
        return "/"

    def items(self, obj):
	ratings = []
	historychanges =  TallstreetHistoryChanges.get_all()
	for historychange in historychanges:
		history = TallstreetHistory.get_or_insert(historychange.key().id_or_name())
		
		logging.debug(history.universe.money)
		history.universe.money += long(round(history.universe.money * (1.0 * history.changes[0] / 100)))
		
		investors = TallstreetPortfolio.get_investors(history.universe.url, history.universe.tag)
		
		logging.debug(history.universe.url.url)
		logging.debug(history.universe.money)
		history.universe.put()
		logging.debug(history.changes)
		for investor in investors:
			update_portfolio_gain(investor.parent(), history.universe.url, history.universe.tag, history.changes[0])
			
		historychange.delete()

	users =  User.need_new_money()		
	for user in users:
		update_new_money(user)
		
	return []
