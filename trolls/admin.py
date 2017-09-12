from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin

from trolls.models import RedditList, RedditPermalink, RedditScrapeCommunity


admin.site.register(RedditList, ResourceAdmin)
admin.site.register(RedditPermalink, ResourceAdmin)
admin.site.register(RedditScrapeCommunity, CommunityAdmin)
