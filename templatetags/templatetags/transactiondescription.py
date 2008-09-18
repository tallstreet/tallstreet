from django import template
import urllib
import re
from ts.search.models import TallstreetUrls

from datetime import datetime, timedelta

trans = re.compile("^(Bought|Sold|Gained|Lost) in \[(url.*)\] under (.*)$")
register = template.Library()
today = datetime.today()
yesterday = today - timedelta(1)
 
 
@register.filter()
def transactiondescription(value):
	values = trans.findall(value)[0]
	if values[0] == "Lost":
		desc = '<img src="/media/images/down.gif" width="11" height="13" border="0">'
	elif values[0] == "Gained":
		desc = '<img src="/media/images/up.gif" width="11" height="13" border="0">'
	else:
		desc = values[0]
	desc += " in "
	dburl = TallstreetUrls.get_or_insert(values[1])
	desc += '<a href="%s" target=_blank>%s</a>' % (dburl.url, dburl.title)
	desc += ' under '
	desc += '<a href="%s" target=_blank>%s</a>' % (tallstreetlink(values[2]), values[2])
	return desc
	
@register.filter()
def display_history(value):
	if not value:
		return ""
	history = value.get()
	last_change = history.changes[0]
	last_change_date = history.dates[0]
	if (last_change_date < yesterday):
		change_age = "changeli_age"
	else:
		change_age = "changeli"
		
	if last_change > 0:
		change = "up.gif"
	else:
		change = "down.gif"
		
	if last_change == 0:
		return ""
	else:
		return '<li class="%s"><img src="/media/images/%s" width="11" height="13" border="0"> %s</li>' % (change_age, change, str(last_change) + "%")
	
	


@register.filter()
def tallstreetlink(value):
	if value:
		return "/view/" + value.replace(" ", "_") + "/"
	else:
		return ""	

@register.filter()
def tallstreetinvestlink(value):
	if value:
		return "/invest/" + urllib.quote(value)
	else:
		return ""