from __future__ import unicode_literals, absolute_import, print_function, division
import six

import re

from core.processors.base import Processor
from core.models.organisms import Collective


class ExpansionProcessor(Processor):

    def collective_content(self, individuals):

        individuals = list(individuals)
        updates = {}
        pattern = re.compile("/data/v\d+/collective/(?P<collective_id>\d+)/?(content/)?")
        for ind in individuals:
            for key, value in six.iteritems(ind):
                if isinstance(value, six.string_types) and value.startswith("/data/"):
                    match = pattern.match(value)
                    if match is not None:
                        updates[(key, match.group("collective_id"),)] = ind

        # TODO: make this a true generator and do not traverse the whole list to gather nested collectives?
        qs = Collective.objects.prefetch_related("individual_set").filter(pk__in=[int(pk) for prop, pk in six.iterkeys(updates)])
        collectives = {
            collective.id: collective
            for collective in qs
        }

        for key, value in six.iteritems(updates):
            prop, pk = key
            value[prop] = list(collectives[int(pk)].content)

        return (individual for individual in individuals)