from django.contrib import admin

from apps.models import Webapp


class WebappAdmin(admin.ModelAdmin):
    list_display = ("route", "language",)


admin.site.register(Webapp, WebappAdmin)
