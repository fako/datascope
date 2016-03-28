from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from visual_translations.models import VisualTranslationsEUCommunity


admin.site.register(VisualTranslationsEUCommunity, CommunityAdmin)
