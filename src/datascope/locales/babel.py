import django
from jinja2.ext import babel_extract as jinja_babel_extract

django.setup()


def babel_extract(fileobj, keywords, comment_tags, options):
    from django.template import engines
    options['extensions'] = ",".join(engines['jinja2'].env.extensions.keys())
    return jinja_babel_extract(fileobj, keywords, comment_tags, options)
