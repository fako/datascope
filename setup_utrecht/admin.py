from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin

from setup_utrecht.models import UniformImagesCommunity, RedditList, RedditPermalink, RedditScrapeCommunity


admin.site.register(RedditList, ResourceAdmin)
admin.site.register(RedditPermalink, ResourceAdmin)
admin.site.register(RedditScrapeCommunity, CommunityAdmin)

admin.site.register(UniformImagesCommunity, CommunityAdmin)
