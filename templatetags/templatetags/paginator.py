from django.template import Library

register = Library()

# http://www.djangosnippets.org/snippets/73/
@register.inclusion_tag('paginator.html', takes_context=True)
def paginator(context, adjacent_pages=5):
    results_per_page = context['results_per_page']
    left_results= context['hits'] - context['last_on_page']
    next_per_page = left_results < results_per_page and left_results or results_per_page

    page_numbers = [n for n in  range(context['page'] - adjacent_pages, context['page'] + adjacent_pages + 1) if n > 0 and n <= context['pages']]
    ctx = {
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
        'next_per_page': next_per_page,
    }
    if context.has_key('paginator_param'):
        ctx['paginator_param'] = context['paginator_param']
    return ctx
