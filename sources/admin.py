from __future__ import unicode_literals, absolute_import, print_function, division

from django.contrib import admin

from core.admin.resources import ResourceAdmin
from sources.models import GoogleImage, WikipediaTranslate


admin.site.register(WikipediaTranslate, ResourceAdmin)
admin.site.register(GoogleImage, ResourceAdmin)
