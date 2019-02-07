from django.contrib import admin


class ShellResourceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uri', 'status', 'stderr', 'config', 'created_at', 'modified_at']
    search_fields = ['uri', 'stdout', 'stderr']
