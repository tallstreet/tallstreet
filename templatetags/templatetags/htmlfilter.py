from util.BeautifulSoup import BeautifulSoup, Comment
from django.template import Library

register = Library()


def sanitize_html(value):
    valid_tags = ''.split()
    valid_attrs = ''.split()
    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                     if attr in valid_attrs]
    return soup.renderContents().decode('utf8').replace('javascript:', '')

register.filter('santize_html', sanitize_html)
