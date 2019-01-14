from django.contrib import admin

from core.admin.resources import ResourceAdmin
from sources.models import (GoogleImage, WikipediaTranslate, GoogleTranslate, ImageDownload, WikipediaRecentChanges,
                            WikipediaListPages, WikiDataItems, WikipediaTransclusions, WikipediaRevisions,
                            WikipediaSearch, WikipediaCategoryMembers, WikipediaCategories, KledingListing, GoogleText)


admin.site.register(WikipediaTranslate, ResourceAdmin)
admin.site.register(GoogleImage, ResourceAdmin)
admin.site.register(GoogleTranslate, ResourceAdmin)
admin.site.register(ImageDownload, ResourceAdmin)
admin.site.register(WikipediaRecentChanges, ResourceAdmin)
admin.site.register(WikipediaListPages, ResourceAdmin)
admin.site.register(WikiDataItems, ResourceAdmin)
admin.site.register(WikipediaTransclusions, ResourceAdmin)
admin.site.register(WikipediaRevisions, ResourceAdmin)
admin.site.register(WikipediaSearch, ResourceAdmin)
admin.site.register(WikipediaCategoryMembers, ResourceAdmin)
admin.site.register(WikipediaCategories, ResourceAdmin)
admin.site.register(KledingListing, ResourceAdmin)
admin.site.register(GoogleText, ResourceAdmin)
