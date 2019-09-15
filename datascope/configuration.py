from django.conf import settings

from datagrowth.configuration import DEFAULT_CONFIGURATION


PROCESS_CHOICE_LIST = [
    ("HttpResourceProcessor.fetch", "Fetch content from HTTP resource"),
    ("HttpResourceProcessor.fetch_mass", "Fetch content from multiple HTTP resources"),
    ("ExtractProcessor.extract_from_resource", "Extract content from one or more resources"),
    ("ExtractProcessor.pass_resource_through", "Take content 'as is' from one or more resources"),
]


MOCK_CONFIGURATION = {
    # testing basic functionality
    "name_namespace_configuration": "namespace configuration",
    "global_global_configuration": "global configuration",
    "global_user_agent": "DataGrowth (test)",
    "global_token": "",
    "global_purge_immediately": False,
    "global_sample_size": 0,
    "global_cache_only": False,
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
