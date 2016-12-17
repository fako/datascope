from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from similarity.models import WikipediaCategorySimularityCommunity


admin.site.register(WikipediaCategorySimularityCommunity, CommunityAdmin)
