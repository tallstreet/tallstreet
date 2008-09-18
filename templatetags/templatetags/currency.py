from django import template
import locale
locale.setlocale(locale.LC_ALL, '')
register = template.Library()
 
 
@register.filter()
def currency(value):
    return locale.format("%d", value, 1)

