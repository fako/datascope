from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from online_discourse.models import DiscourseSearchCommunity


admin.site.register(DiscourseSearchCommunity, CommunityAdmin)
