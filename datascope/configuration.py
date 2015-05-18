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

    "http_resource_batch_size": 0,
    "http_resource_continuation_limit": 1,

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
}