# -*- coding: utf8 -*-
#from django.conf import settings
from django.template import Library
import re
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = Library()

@register.filter
def plaintext2html(text, autoescape=None):
    tabstop=4
    re_string = re.compile(r'(?P<htmlchars>[<&>\'"])|(?P<space>^[ \t]+)|(?P<lineend>\r\n|\r|\n)|(?P<protocol>((https|http|ftp)://.*?))([^\x00-\xff]|\s|$|")', re.S|re.M|re.I)
    def do_sub(m):
        c = m.groupdict()
        if c['htmlchars']:
            if autoescape:
                esc = conditional_escape
            else:
                esc = lambda x: x
            return esc(c['htmlchars'])
        if c['lineend']:
            return '<br/>'
        elif c['space']:
            t = m.group().replace('\t', '&nbsp;'*tabstop)
            t = t.replace(' ', '&nbsp;')
            return t
        elif c['space'] == '\t':
            return ' '*tabstop;
        else:
            url = m.group('protocol')
            if url.startswith(' '):
                prefix = ' '
                url = url[1:]
            else:
                prefix = ''
            last = m.groups()[-1]
            if last in ['\n', '\r', '\r\n']:
                last = '<br/>'
            #if len(url)>settings.LINK_MAX_LENGTH:
             #   link_text = '%s...' % url[:settings.LINK_MAX_LENGTH]
            #else:
            link_text = url
            return '%s<a href="%s">%s</a>%s' % (prefix, url, link_text, last)
    result =  re.sub(re_string, do_sub, text)
    return mark_safe(result)

plaintext2html.needs_autoescape = True