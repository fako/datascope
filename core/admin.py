from django.contrib import admin

from core.models import TextStorage, ProcessStorage, VisualTranslationsStorage, PeopleSuggestionsStorage


class TextStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'head', 'body', 'created_at']
    search_fields = ['identity', 'arguments', 'configuration']


class ProcessStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'results', 'exception', 'traceback', 'created_at', 'modified_at']
    search_fields = ['identity', 'arguments', 'configuration']


admin.site.register(TextStorage, TextStorageAdmin)
admin.site.register(ProcessStorage, ProcessStorageAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'content', 'views', 'created_at', 'completed_at', 'modified_at', 'purge_at']
    search_fields = ['identity', 'arguments', 'configuration']


admin.site.register(VisualTranslationsStorage, ServiceAdmin)
admin.site.register(PeopleSuggestionsStorage, ServiceAdmin)
