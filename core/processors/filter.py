from django.db.models.query import Q

from core.processors.base import QuerySetProcessor
from datagrowth.datatypes import DocumentPostgres


class FilterProcessor(QuerySetProcessor):

    def get_query_filter_for_postgres(self, criteria):
        query_filter = Q()
        for key, values in criteria.items():
            for value in values:
                query_filter |= Q(**{"properties__{}".format(key): value})
        return query_filter

    def get_query_filter_for_non_postgres(self, criteria):
        query_filter = Q()
        for key, values in criteria.items():
            for value in values:
                query_filter |= Q(properties__contains='{}": "{}'.format(key, value))
        return query_filter

    def filter(self, query_set):
        criteria = {
            key: self.config.get(key).split("|") for key in self.config.select_keys
            if self.config.get(key, None)
        }
        query_filter = self.get_query_filter_for_postgres(criteria) if issubclass(query_set.model, DocumentPostgres) \
            else self.get_query_filter_for_non_postgres(criteria)
        return query_set.filter(query_filter)
