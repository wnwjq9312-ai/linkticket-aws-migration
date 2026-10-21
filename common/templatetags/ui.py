from django import template
from django.templatetags.static import static
register = template.Library()

@register.filter
def image_url(value):
    """Stored media URLs and packaged static assets share a template contract."""
    if not value:
        return ''
    value = str(value)
    return value if value.startswith('/') and not value.startswith('//') else static(value)

@register.simple_tag(takes_context=True)
def page_link(context, number, parameter='page'):
    query = context['request'].GET.copy()
    query[parameter] = number
    return '?' + query.urlencode()

@register.simple_tag
def page_numbers(page):
    return page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
