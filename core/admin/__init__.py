from django.contrib import admin

from .organisms import OrganismAdmin, CollectiveAdmin
from core.models.organisms import Individual, Collective, Growth


admin.site.register(Individual, OrganismAdmin)
admin.site.register(Collective, CollectiveAdmin)
