from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from core.admin.organisms import CommunityAdmin

from setup_utrecht.models import (UniformImagesCommunity, UniformImageDownload, RedditList, RedditPermalink,
                                  RedditScrapeCommunity, RedditImageDownload)


admin.site.register(RedditList, HttpResourceAdmin)
admin.site.register(RedditPermalink, HttpResourceAdmin)
admin.site.register(RedditImageDownload, HttpResourceAdmin)
admin.site.register(RedditScrapeCommunity, CommunityAdmin)

admin.site.register(UniformImagesCommunity, CommunityAdmin)
admin.site.register(UniformImageDownload, HttpResourceAdmin)
