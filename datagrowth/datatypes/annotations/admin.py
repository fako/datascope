from django.contrib import admin


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "annotation", "user", "created_at", "modified_at")
    search_fields = ("reference", "string",)
