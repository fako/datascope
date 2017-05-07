from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from topic_research.models import WikipediaCategorySimularityCommunity, CrossCombineTermSearchCommunity


admin.site.register(WikipediaCategorySimularityCommunity, CommunityAdmin)
admin.site.register(CrossCombineTermSearchCommunity, CommunityAdmin)
