from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from wiki_feed.models import WikiFeedCommunity, WikiFeedUsageCommunity


admin.site.register(WikiFeedCommunity, CommunityAdmin)
admin.site.register(WikiFeedUsageCommunity, CommunityAdmin)
