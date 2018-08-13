from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin
from topic_research.models import WikipediaCategorySimularityCommunity, WebTextResource


admin.site.register(WikipediaCategorySimularityCommunity, CommunityAdmin)
admin.site.register(WebTextResource, ResourceAdmin)
