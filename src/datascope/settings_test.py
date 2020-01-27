from .settings_base import *


DATASCOPE_VERSION = "0.0.0"
MAX_BATCH_SIZE = None  # better for sqlite to let Django determine batch size
STATIC_IP = "127.0.0.1"
USE_MOCKS = True
DEBUG_TOOLBAR = True

LOGGING["loggers"] = {}

if os.environ.get('TRAVIS_TEST_DATABASE'):
    del DATABASES["default"]["PASSWORD"]

MIGRATION_MODULES = {
    'auth': None,
    'contenttypes': None,
    'default': None,
    'sessions': None,

    'datascope': None,
    'core': None,
    'sources': None,
    'wiki_feed': None,
    'visual_translations': None,
    'future_fashion': None,
    'open_data': None,
    'wiki_scope': None,
    'online_discourse': None,
    'nautilus': None,
    'setup_utrecht': None,
}

DATAGROWTH_DEFAULT_CONFIGURATION = {
    # testing basic functionality
    "name_namespace_configuration": "namespace configuration",
    "global_global_configuration": "global configuration",
    "global_async": True,
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
