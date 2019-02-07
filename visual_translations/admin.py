from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin
from core.admin.organisms import CommunityAdmin
from visual_translations.models import VisualTranslationsEUCommunity, VisualTranslationsBRICCommunity, WebImageDownload


admin.site.register(VisualTranslationsEUCommunity, CommunityAdmin)
admin.site.register(VisualTranslationsBRICCommunity, CommunityAdmin)
admin.site.register(WebImageDownload, HttpResourceAdmin)
