import os

from django.conf import settings


######################################
# PLAIN SETTINGS
######################################


DATAGROWTH_DATETIME_FORMAT = getattr(settings, "DATAGROWTH_DATETIME_FORMAT", "%Y%m%d%H%M%S%f")

DATAGROWTH_DATA_DIR = getattr(settings, "DATAGROWTH_DATA_DIR", os.path.join(settings.BASE_DIR, "data"))
DATAGROWTH_MEDIA_ROOT = getattr(settings, "DATAGROWTH_MEDIA_ROOT", settings.MEDIA_ROOT)
DATAGROWTH_BIN_DIR = getattr(settings, "DATAGROWTH_BIN_DIR",
    os.path.join(settings.BASE_DIR, "datagrowth", "resources", "shell", "bin")
)

DATAGROWTH_REQUESTS_PROXIES = getattr(settings, "DATAGROWTH_REQUESTS_PROXIES", None)
DATAGROWTH_REQUESTS_VERIFY = getattr(settings, "DATAGROWTH_REQUESTS_VERIFY", True)


######################################
# DEFAULT CONFIGURATION SETTINGS
######################################


DATAGROWTH_DEFAULT_CONFIGURATION = getattr(settings, "DATAGROWTH_DEFAULT_CONFIGURATION", {
    "global_async": True,  # by default offload to celery where possible
    "global_user_agent": "DataScope (v{})".format(settings.DATASCOPE_VERSION),
    "global_token": "",
    "global_purge_immediately": False,  # by default keep resources around
    "global_sample_size": 0,
    "global_fetch_only": False,  # TODO: implement for Resource, cache_only is a better name, pol-harvester dependency

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
    "rank_processor_result_size": 20,

    "micro_service_connections": {
        "image_recognition": {
            "protocol": "http",
            "host": "localhost:2000",
            "path": "/predict/"
        },
        "clothing_type_recognition": {
            "protocol": "http",
            "host": "localhost:2001",
            "path": "/predict/"
        }
    }
})


DATAGROWTH_MOCK_CONFIGURATION = {
    # testing basic functionality
    "name_namespace_configuration": "namespace configuration",
    "global_global_configuration": "global configuration",
    "global_user_agent": "DataScope (test)",
    "global_token": "",
    "global_purge_immediately": False,
    "global_sample_size": 0,
    "global_fetch_only": False,
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
    # micro services
    "micro_service_connections": {
        "mock_service": {
            "protocol": "http",
            "host": "localhost:2000",
            "path": "/service/"
        }
    }
}
