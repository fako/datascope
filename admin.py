from django.contrib import admin

from HIF.models import DataLink, DataProcess


class DataLinkAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','response']

class DataProcessAdmin(admin.ModelAdmin):
    list_display = ['args','kwargs','results']

admin.site.register(DataLink, DataLinkAdmin)
admin.site.register(DataProcess, DataProcessAdmin)
