from django.contrib import admin

from datagrowth.admin import HttpResourceAdmin, ShellResourceAdmin, DocumentAdmin, DataStorageAdmin
from core.admin.organisms import CommunityAdmin
from online_discourse.models import (DiscourseSearchCommunity, DiscourseOrder, ComplexityAnalysis, WebTextResource,
                                     WebContentDownload, WebTextTikaResource, Collection, Document, ElasticIndex)


class DiscourseOrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "email", "topic", "created_at")


class ElasticIndexAdmin(admin.ModelAdmin):
    list_display = ("signature", "remote_name", "remote_exists", "error_count", "language", "created_at", "modified_at",)


admin.site.register(DiscourseSearchCommunity, CommunityAdmin)
admin.site.register(DiscourseOrder, DiscourseOrderAdmin)
admin.site.register(ComplexityAnalysis, HttpResourceAdmin)
admin.site.register(WebTextResource, HttpResourceAdmin)
admin.site.register(WebContentDownload, HttpResourceAdmin)
admin.site.register(WebTextTikaResource, ShellResourceAdmin)
admin.site.register(Collection, DataStorageAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(ElasticIndex, ElasticIndexAdmin)
