from django.contrib import admin

from HIF.models import TextStorage, ProcessStorage


class TextStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','head','body']

class ProcessStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','results']

admin.site.register(TextStorage, TextStorageAdmin)
admin.site.register(ProcessStorage, ProcessStorageAdmin)
