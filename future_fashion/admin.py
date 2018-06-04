from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from future_fashion.models import FutureFashionCommunity, InventoryCommunity


admin.site.register(FutureFashionCommunity, CommunityAdmin)
admin.site.register(InventoryCommunity, CommunityAdmin)
