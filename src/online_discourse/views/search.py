from copy import copy

from django.shortcuts import Http404
from rest_framework import views
from rest_framework.response import Response

from core.views import CommunityView
from online_discourse.elastic import get_es_client
from online_discourse.models import ElasticIndex


class DiscourseSearchView(views.APIView):

    elastic = get_es_client(silent=True)

    @classmethod
    def get_query_body(cls, text=None, authors=None, sources=None):
        query = {"bool": {"must": []}}
        # Adding full text search
        if text and text[0]:  # bit of a hack because frontend might send: [""]
            query["bool"]["must"].append({
                "multi_match": {
                    "query": " ".join(text),
                    "fields": ["content", "title"]
                }
            })
        # Adding term filters
        if authors:
            query["bool"]["must"].append({"terms": {"author": authors.split("|")}})
        if sources:
            query["bool"]["must"].append({"terms": {"source": sources.split("|")}})
        # We always query with a score modification for the argument_score
        return {
            "query": {
                "function_score": {
                    "query": query,
                    "field_value_factor": {
                        "field": "argument_score",
                        "factor": 1.0,
                        "missing": 0.0001
                    },
                    "boost_mode": "multiply"
                }

            },
            "from": 0,
            "size": 60
        }

    def get_index_or_raise(self, configuration, community_class, path):
        signature = community_class.get_signature_from_input(
            *path.split('/'),
            **configuration
        )
        try:
            return ElasticIndex.objects.filter(signature=signature).latest("created_at")
        except ElasticIndex.DoesNotExist:
            raise Http404("Can not find index with signature=".format(signature))

    def get_response_from_results(self, results):
        hits = results["hits"]["hits"]
        response_data = copy(CommunityView.RESPONSE_DATA)
        documents = []
        for hit in hits:
            document = hit["_source"]
            document["_id"] = hit["_id"]
            documents.append(document)
        response_data["results"] = documents
        return Response(response_data)

    def get(self, request, community_class, path=""):
        configuration, created_at_info = CommunityView.get_configuration_from_request(request)
        body = self.get_query_body()
        index = self.get_index_or_raise(configuration, community_class, path)
        results = self.elastic.search(
            body=body,
            index=index.remote_name,
            _source=["title", "url", "author", "source", "argument_score"]
        )
        return self.get_response_from_results(results)

    def post(self, request, community_class, path=""):
        configuration, created_at_info = CommunityView.get_configuration_from_request(request)
        body = self.get_query_body(
            text=configuration.get("keywords", []),
            authors=configuration.get("author", None),
            sources=configuration.get("source", None)
        )
        index = self.get_index_or_raise(configuration, community_class, path)
        results = self.elastic.search(
            body=body,
            index=index.remote_name,
            _source=["title", "url", "author", "source", "argument_score"]
        )
        return self.get_response_from_results(results)
