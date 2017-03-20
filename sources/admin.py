from django.contrib import admin

from core.admin.resources import ResourceAdmin
from sources.models import (GoogleImage, WikipediaTranslate, GoogleTranslate, ImageDownload, WikipediaRecentChanges,
                            WikipediaListPages, WikiDataItems, ImageFeatures, WikipediaTransclusions,
                            WikipediaRevisions, OfficialAnnouncementsNetherlands,
                            OfficialAnnouncementsDocumentNetherlands)


admin.site.register(WikipediaTranslate, ResourceAdmin)
admin.site.register(GoogleImage, ResourceAdmin)
admin.site.register(GoogleTranslate, ResourceAdmin)
admin.site.register(ImageDownload, ResourceAdmin)
admin.site.register(WikipediaRecentChanges, ResourceAdmin)
admin.site.register(WikipediaListPages, ResourceAdmin)
admin.site.register(WikiDataItems, ResourceAdmin)
admin.site.register(ImageFeatures, ResourceAdmin)
admin.site.register(WikipediaTransclusions, ResourceAdmin)
admin.site.register(WikipediaRevisions, ResourceAdmin)
admin.site.register(OfficialAnnouncementsNetherlands, ResourceAdmin)
admin.site.register(OfficialAnnouncementsDocumentNetherlands, ResourceAdmin)
