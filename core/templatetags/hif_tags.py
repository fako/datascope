import math

from django import template
register = template.Library()

@register.simple_tag()
def render_url(url, frm="img"):
    if frm == "img":
        return u'<img src="{}"/>'.format(url)
    elif frm == "yt":
        pass

@register.filter()
def is_list(var):
    return isinstance(var, list)

@register.filter()
def is_url(var):
    return var.startswith('http')

@register.filter()
def span(var):
    return 'span' + str(int(math.floor(12/len(var))))