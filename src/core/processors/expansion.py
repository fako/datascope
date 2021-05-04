import re

from core.processors.base import Processor
from core.models.organisms import Collective


class ExpansionProcessor(Processor):

    def collective_content(self, individuals):

        individuals = list(individuals)
        updates = {}
        pattern = re.compile("/api/v\d+/collective/(?P<collective_id>\d+)/?(content/)?")
        for index, ind in enumerate(individuals):
            for key, value in ind.items():
                if isinstance(value, str) and value.startswith("/api/"):
                    match = pattern.match(value)
                    if match is not None:
                        updates[(index, key, match.group("collective_id"),)] = ind

        # TODO: update this to work with Collections and Documents
        qs = Collective.objects.prefetch_related("individual_set").filter(
            pk__in=[int(pk) for index, prop, pk in updates.keys()]
        )
        collectives = {
            collective.id: collective
            for collective in qs
        }

        for key, value in updates.items():
            index, prop, pk = key
            value[prop] = list(collectives[int(pk)].content)

        return (individual for individual in individuals)
