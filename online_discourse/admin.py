from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin, ShellResourceAdmin
from core.admin.organisms import CommunityAdmin
from online_discourse.models import (DiscourseSearchCommunity, DiscourseOrder, ComplexityAnalysis, WebTextResource,
                                     WebContentDownload, WebTextTikaResource)


class DiscourseOrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "email", "topic", "created_at")


admin.site.register(DiscourseSearchCommunity, CommunityAdmin)
admin.site.register(DiscourseOrder, DiscourseOrderAdmin)
admin.site.register(ComplexityAnalysis, HttpResourceAdmin)
admin.site.register(WebTextResource, HttpResourceAdmin)
admin.site.register(WebContentDownload, HttpResourceAdmin)
admin.site.register(WebTextTikaResource, ShellResourceAdmin)
