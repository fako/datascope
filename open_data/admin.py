from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin
from open_data.models import (DutchParliamentarySeatingTranscriptsCommunity, OfficialAnnouncementsNetherlands,
                              OfficialAnnouncementsDocumentNetherlands)


admin.site.register(DutchParliamentarySeatingTranscriptsCommunity, CommunityAdmin)
admin.site.register(OfficialAnnouncementsNetherlands, ResourceAdmin)
admin.site.register(OfficialAnnouncementsDocumentNetherlands, ResourceAdmin)
