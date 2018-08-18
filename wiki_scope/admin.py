from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from wiki_scope.models import WikipediaCategorySimilarityCommunity


admin.site.register(WikipediaCategorySimilarityCommunity, CommunityAdmin)
