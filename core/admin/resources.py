from __future__ import unicode_literals, absolute_import, print_function, division

from django.contrib import admin


class ResourceAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'uri', 'data_hash', 'status', 'config', 'created_at', 'modified_at']
