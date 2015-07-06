from __future__ import unicode_literals, absolute_import, print_function, division
import six

import re

from core.models.organisms import Collective

class ExpansionProcessor(object):

    def __init__(self, *args, **kwargs):
        super(ExpansionProcessor, self).__init__()

    def collective_content(self, individuals):

        updates = {}
        pattern = re.compile("/data/v\d+/collective/(?P<collective_id>\d+)/?(content/)?")
        for ind in individuals:
            for key, value in six.iteritems(ind):
                if isinstance(value, six.string_types) and value.startswith("/data/"):
                    match = pattern.match(value)
                    if match is not None:
                        updates[(key, match.group("collective_id"),)] = ind

        collectives = Collective.objects.filter(pk__in=[int(pk) for prop, pk in six.iterkeys(updates)])
        for key, value in six.iteritems(updates):
            prop, pk = key
            value[prop] = collectives.get(pk=pk).content

        return individuals