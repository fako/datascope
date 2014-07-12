from django.conf import settings

# Settings for HIF come from the Domain class.
# Later it will be easy to load configs out of the db.
class Domain(object):

    #HIF__supported_languages = ['en','nl','pt','de','fr','es']
    HIF__supported_languages = ['zh','ru','pt']
    HIF_debug = True
    HIF_allowed_origins = [
        'http://localhost:9000',
        'http://127.0.0.1:9000',
    ]

    TEST_skip_external_resource_integration = settings.HIF_SKIP_EXTERNAL_RESOURCE_INTEGRATION_TESTS
    TEST_query = "cow"

    google_key = settings.GOOGLE_API_KEY
    google_cx = '004613812033868156538:5pcwbuudj1m'

    wiki_source_language = 'en'
    wiki_translate_to = 'pt'

