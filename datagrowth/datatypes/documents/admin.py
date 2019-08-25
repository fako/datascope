from django.contrib import admin


class DataStorageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'created_at', 'modified_at']


class DocumentAdmin(DataStorageAdmin):
    search_fields = ["properties"]
