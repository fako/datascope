from django.contrib import admin


class HttpResourceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uri', 'status', 'config', 'created_at', 'modified_at']
    search_fields = ['uri', 'head', 'body']
