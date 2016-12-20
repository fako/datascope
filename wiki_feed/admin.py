from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from wiki_feed.models import WikiFeedCommunity


admin.site.register(WikiFeedCommunity, CommunityAdmin)
