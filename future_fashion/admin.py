from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from core.admin.resources import ResourceAdmin
from future_fashion.models import (ClothingDataCommunity, ClothingInventoryCommunity, BrandRecognitionService,
                                   ClothingTypeRecognitionService, ImageFeatures, ColorClothingSet)


class ColorClothingSetAdmin(admin.ModelAdmin):
    list_display = ["email", "processing_permission", "top_item_image", "bottom_item_image", "match_style"]
    readonly_fields = ("processing_permission", "top_item_image", "bottom_item_image",)


admin.site.register(ClothingDataCommunity, CommunityAdmin)
admin.site.register(ClothingInventoryCommunity, CommunityAdmin)
admin.site.register(BrandRecognitionService, ResourceAdmin)
admin.site.register(ClothingTypeRecognitionService, ResourceAdmin)
admin.site.register(ImageFeatures, ResourceAdmin)
admin.site.register(ColorClothingSet, ColorClothingSetAdmin)
