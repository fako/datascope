from __future__ import unicode_literals, absolute_import, print_function, division

from django.conf import settings


DEFAULT_CONFIGURATION = {
    "global_allowed_origins": [
        'http://localhost:9000',
        'http://127.0.0.1:9000',
        'http://10.0.2.2:9000',
        'http://data-scope.com',
        'http://data-scope.org',
        'http://globe-scope.com',
        'http://globe-scope.org',
    ],
    "global_async": True,  # by default offload to celery where possible

    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,
    "http_resource_interval_duration": 0,  # NB: milliseconds!
    "http_resource_concat_args_size": 0,
    "http_resource_concat_args_symbol": "|",

    "wikipedia_wiki_country": "en",
    "wikipedia_wiki_query_param": "titles",
    "wikipedia_wiki_full_extracts": False,

    "google_api_key": settings.GOOGLE_API_KEY,
    "google_cx": "004613812033868156538:5pcwbuudj1m"
}


MOCK_CONFIGURATION = {
    # testing basic functionality
    "name_namespace_configuration": "namespace configuration",
    "global_global_configuration": "global configuration",
    # mock configuration for testing HttpResourceMock
    "global_source_language": "en",
    "mock_secret": "oehhh",
    # HttpResource (processor)
    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,
    "http_resource_interval_duration": 0,  # NB: milliseconds!
    "http_resource_concat_args_size": 0,
    "http_resource_concat_args_symbol": "|"
}


PROCESS_CHOICE_LIST = [
    ("HttpResourceProcessor.fetch", "Fetch content from HTTP resource"),
    ("HttpResourceProcessor.fetch_mass", "Fetch content from multiple HTTP resources"),
    ("ExtractProcessor.extract_from_resource", "Extract content from one or more resources"),
]