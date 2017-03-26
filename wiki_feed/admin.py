from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from wiki_feed.models import WikiFeedCommunity, WikiFeedPublishCommunity


admin.site.register(WikiFeedCommunity, CommunityAdmin)
admin.site.register(WikiFeedPublishCommunity, CommunityAdmin)
