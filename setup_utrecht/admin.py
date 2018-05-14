from django.contrib import admin

from core.admin.organisms import CommunityAdmin

from setup_utrecht.models import UniformImagesCommunity


admin.site.register(UniformImagesCommunity, CommunityAdmin)
