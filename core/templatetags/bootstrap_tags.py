import math

from django import template
register = template.Library()


@register.filter()
def col_md(var):
    return 'col-md-' + str(int(math.floor(12/len(var))))
