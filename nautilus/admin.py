from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin

from nautilus.models import LocaforaLogin, LocaforaOrders, LocaforaOrderOverviewCommunity


admin.site.register(LocaforaLogin, ResourceAdmin)
admin.site.register(LocaforaOrders, ResourceAdmin)
admin.site.register(LocaforaOrderOverviewCommunity, CommunityAdmin)
