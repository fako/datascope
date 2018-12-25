from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from core.admin.organisms import CommunityAdmin
from future_fashion.models import (ClothingDataCommunity, ClothingInventoryCommunity, BrandRecognitionService,
                                   ClothingTypeRecognitionService, ImageFeatures, ColorClothingSet,
                                   ClothingImageDownload)


class ColorClothingSetAdmin(admin.ModelAdmin):
    list_display = ["email", "processing_permission", "top_item_image", "bottom_item_image", "created_at"]
    readonly_fields = ("processing_permission", "top_item_image", "bottom_item_image",)


admin.site.register(ClothingDataCommunity, CommunityAdmin)
admin.site.register(ClothingInventoryCommunity, CommunityAdmin)
admin.site.register(BrandRecognitionService, HttpResourceAdmin)
admin.site.register(ClothingTypeRecognitionService, HttpResourceAdmin)
admin.site.register(ImageFeatures, HttpResourceAdmin)
admin.site.register(ColorClothingSet, ColorClothingSetAdmin)
admin.site.register(ClothingImageDownload, HttpResourceAdmin)
