from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from wiki_news.models import WikiNewsCommunity


admin.site.register(WikiNewsCommunity, CommunityAdmin)
