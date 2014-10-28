from django.contrib import admin

from core.models import TextStorage, ProcessStorage


class TextStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','head','body','created_at']

class ProcessStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__','status','results','exception','traceback','created_at', 'modified_at']

admin.site.register(TextStorage, TextStorageAdmin)
admin.site.register(ProcessStorage, ProcessStorageAdmin)