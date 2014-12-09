import textwrap

from django.contrib import admin

from core.models import (TextStorage, ProcessStorage, VisualTranslationsStorage, PeopleSuggestionsStorage,
                         CityCelebritiesStorage, PopularityComparisonStorage)


class TextStorageAdmin(admin.ModelAdmin):
    list_display = ['wrapped_unicode', 'status', 'head', 'body', 'created_at']
    search_fields = ['identity', 'arguments', 'configuration', 'type']

    def wrapped_unicode(self, text_storage):
        return textwrap.fill(unicode(text_storage), 25)
    wrapped_unicode.short_description = 'Text'



class ProcessStorageAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'results', 'exception', 'traceback', 'created_at', 'modified_at']
    search_fields = ['identity', 'arguments', 'configuration', 'type']


admin.site.register(TextStorage, TextStorageAdmin)
admin.site.register(ProcessStorage, ProcessStorageAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'status', 'content', 'views', 'created_at', 'completed_at', 'modified_at', 'purge_at']
    search_fields = ['identity', 'arguments', 'configuration']


admin.site.register(VisualTranslationsStorage, ServiceAdmin)
admin.site.register(PeopleSuggestionsStorage, ServiceAdmin)
admin.site.register(CityCelebritiesStorage, ServiceAdmin)
admin.site.register(PopularityComparisonStorage, ServiceAdmin)
