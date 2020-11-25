from elasticsearch import Elasticsearch

from django.conf import settings


def get_es_client(silent=False):
    """
    Returns the elasticsearch client which uses the configuration file
    """
    es_client = Elasticsearch([settings.ELASTIC_SEARCH_HOST],
                              scheme='http',
                              port=9200,
                              http_compress=True)
    # test if it works
    if not silent and not es_client.cat.health(request_timeout=30):
        raise ValueError('Credentials do not work for Elastic search')
    return es_client


def get_index_config(lang):
    """
    Returns the elasticsearch index configuration.
    Configures the analysers based on the language passed in.
    """
    return {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        },
        'mappings': {
            '_doc': {
                'properties': {
                    'title': {
                        'type': 'text',
                        'analyzer': settings.ELASTIC_SEARCH_ANALYSERS[lang]
                    },
                    'content': {
                        'type': 'text',
                        'analyzer': settings.ELASTIC_SEARCH_ANALYSERS[lang]
                    },
                    'url': {'type': 'text'},
                    'title_plain': {'type': 'text'},
                    'content_plain': {'type': 'text'},
                    'author': {
                        'type': 'keyword'
                    },
                    'source': {
                        'type': 'keyword'
                    },
                    'argument_score': {
                        'type': 'float'
                    }
                }
            }
        }
    }
