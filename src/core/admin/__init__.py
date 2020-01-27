from django.contrib import admin

from .organisms import CollectiveAdmin, GrowthAdmin, IndividualAdmin
from core.models.organisms import Individual, Collective, Growth


admin.site.register(Individual, IndividualAdmin)
admin.site.register(Collective, CollectiveAdmin)
admin.site.register(Growth, GrowthAdmin)
