from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from open_data.models import DutchParliamentarySeatingTranscriptsCommunity


admin.site.register(DutchParliamentarySeatingTranscriptsCommunity, CommunityAdmin)
