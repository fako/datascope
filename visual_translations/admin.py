from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from visual_translations.models import VisualTranslationCommunity


admin.site.register(VisualTranslationCommunity, CommunityAdmin)
