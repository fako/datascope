from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from visual_translations.models import VisualTranslationsCommunity


admin.site.register(VisualTranslationsCommunity, CommunityAdmin)
