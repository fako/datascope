from __future__ import unicode_literals, absolute_import, print_function, division

from django.contrib import admin

from core.admin.resources import ResourceAdmin
from sources.models import (GoogleImage, WikipediaTranslate, GoogleTranslate, ImageDownload, WikipediaRecentChanges,
                            WikipediaListPages, WikiDataItems, ImageFeatures, WikipediaTransclusions)


admin.site.register(WikipediaTranslate, ResourceAdmin)
admin.site.register(GoogleImage, ResourceAdmin)
admin.site.register(GoogleTranslate, ResourceAdmin)
admin.site.register(ImageDownload, ResourceAdmin)
admin.site.register(WikipediaRecentChanges, ResourceAdmin)
admin.site.register(WikipediaListPages, ResourceAdmin)
admin.site.register(WikiDataItems, ResourceAdmin)
admin.site.register(ImageFeatures, ResourceAdmin)
admin.site.register(WikipediaTransclusions, ResourceAdmin)
