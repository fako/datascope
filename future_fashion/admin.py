from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin
from future_fashion.models import (FutureFashionCommunity, InventoryCommunity, BrandRecognitionService,
                                   ClothingTypeRecognitionService, ImageFeatures)


admin.site.register(FutureFashionCommunity, CommunityAdmin)
admin.site.register(InventoryCommunity, CommunityAdmin)
admin.site.register(BrandRecognitionService, ResourceAdmin)
admin.site.register(ClothingTypeRecognitionService, ResourceAdmin)
admin.site.register(ImageFeatures, ResourceAdmin)
