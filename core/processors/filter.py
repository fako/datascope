from django.db.models.query import Q

from core.processors.base import QuerySetProcessor


class FilterProcessor(QuerySetProcessor):

    def filter(self, query_set):
        criteria = {
            key: self.config.get(key).split("|") for key in self.config.select_keys
            if self.config.get(key, None)
        }
        query_filter = Q()
        for key, values in criteria.items():
            for value in values:
                query_filter |= Q(properties__contains='{}": "{}'.format(key, value))
        return query_set.filter(query_filter)
