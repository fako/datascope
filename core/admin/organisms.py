import humanize

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from core.models import Individual, Growth
from core.models.resources.manifestation import Manifestation


class IndividualInline(admin.StackedInline):
    model = Individual
    fields = ("properties",)
    extra = 0


class OrganismAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'size', 'created_at', 'modified_at']

    def size(self, organism):
        return humanize.naturalsize(len(organism.json_content))


class IndividualAdmin(OrganismAdmin):
    search_fields = ["properties"]


class CollectiveAdmin(OrganismAdmin):
    inlines = [IndividualInline]


class GrowthInline(GenericStackedInline):
    model = Growth
    fields = ("type", "state", "config",)
    extra = 0
    ct_field = "community_type"
    ct_fk_field = "community_id"


class GrowthAdmin(admin.ModelAdmin):
    list_display = ["type", "state", "config"]


class ManifestationInline(GenericStackedInline):
    model = Manifestation
    readonly_fields = ("created_at", "completed_at")
    fields = ("uri", "config", "created_at", "completed_at", "task", "data")
    extra = 0
    ct_field = "community_type"
    ct_fk_field = "community_id"


class CommunityAdmin(admin.ModelAdmin):
    list_display = ["__str__", "signature", "state", "views", "config"]
    readonly_fields = ("created_at", "modified_at", "current_growth")
    inlines = (
        GrowthInline,
        ManifestationInline
    )
