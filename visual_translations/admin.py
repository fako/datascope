from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from visual_translations.models import VisualTranslationsEUCommunity, VisualTranslationsBRICCommunity


admin.site.register(VisualTranslationsEUCommunity, CommunityAdmin)
admin.site.register(VisualTranslationsBRICCommunity, CommunityAdmin)
