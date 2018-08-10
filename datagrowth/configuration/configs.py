from django.conf import settings


DEFAULT_CONFIGURATION = {
    "global_allowed_origins": [
        'http://localhost:9000',
        'http://127.0.0.1:9000',
        'http://10.0.2.2:9000',
        'http://data-scope.com',
        'http://www.data-scope.com',
        'https://data-scope.com',
        'https://www.data-scope.com',
        'http://globe-scope.com',
        'http://www.globe-scope.com',
        'http://debatkijker.nl',
        'http://www.debatkijker.nl',
    ],
    "global_async": True,  # by default offload to celery where possible
    "global_user_agent": "DataScope (v{})".format(settings.DATASCOPE_VERSION),
    "global_token": "",
    "global_purge_immediately": False,  # by default keep resources around
    "global_sample_size": 0,

    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,
    "http_resource_interval_duration": 0,  # NB: milliseconds!
    "http_resource_concat_args_size": 0,
    "http_resource_concat_args_symbol": "|",

    "wikipedia_wiki_country": "en",
    "wikipedia_wiki_query_param": "titles",
    "wikipedia_wiki_full_extracts": False,
    "wikipedia_wiki_domain": "en.wikipedia.org",
    "wikipedia_wiki_show_categories": "!hidden",

    "google_api_key": getattr(settings, 'GOOGLE_API_KEY', ''),
    "google_cx": "004613812033868156538:5pcwbuudj1m",

    "indico_api_key": getattr(settings, 'INDICO_API_KEY', ''),
    "wizenoze_api_key": getattr(settings, 'WIZENOZE_API_KEY', ''),

    "rank_processor_batch_size": 1000,
    "rank_processor_result_size": 20
}


MOCK_CONFIGURATION = {
    # testing basic functionality
    "name_namespace_configuration": "namespace configuration",
    "global_global_configuration": "global configuration",
    "global_user_agent": "DataScope (test)",
    "global_token": "",
    "global_purge_immediately": False,
    "global_sample_size": 0,
    # mock configuration for testing HttpResourceMock
    "global_source_language": "en",
    "mock_secret": "oehhh",
    # HttpResource (processor)
    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,
    "http_resource_interval_duration": 0,  # NB: milliseconds!
    "http_resource_concat_args_size": 0,
    "http_resource_concat_args_symbol": "|",
    "mock_processor_include_odd": False,
    "mock_processor_include_even": False,
}
