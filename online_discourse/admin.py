from django.contrib import admin

from core.admin.organisms import CommunityAdmin
from online_discourse.models import DiscourseSearchCommunity, DiscourseOrder


class DiscourseOrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "email", "topic", "created_at")


admin.site.register(DiscourseSearchCommunity, CommunityAdmin)
admin.site.register(DiscourseOrder, DiscourseOrderAdmin)
