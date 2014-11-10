from django.contrib import admin

from core.models import TextStorage, ProcessStorage


class TextStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'head', 'body', 'created_at']
    search_fields = ['identity', 'arguments', 'configuration']

class ProcessStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'results', 'exception', 'traceback', 'created_at', 'modified_at']
    search_fields = ['identity', 'arguments', 'configuration']

admin.site.register(TextStorage, TextStorageAdmin)
admin.site.register(ProcessStorage, ProcessStorageAdmin)