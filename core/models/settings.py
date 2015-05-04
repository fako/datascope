from django.conf import settings

# Settings for HIF come from the Domain class.
# Later it will be easy to load configs out of the db.
class Domain(object):

    #HIF__supported_languages = ['en','nl','pt','de','fr','es']
    #HIF__supported_languages = ['zh','ru','pt']
    HIF__supported_languages = ['pl', 'tr', 'id']
    HIF_debug = True
    HIF_allowed_origins = [
        'http://localhost:9000',
        'http://127.0.0.1:9000',
        'http://10.0.2.2:9000',
        'http://data-scope.com',
        'http://data-scope.org',
        'http://globe-scope.com',
        'http://globe-scope.org',
    ]
    HIF_source_language = 'en'

    TEST_skip_external_resource_integration = settings.HIF_SKIP_EXTERNAL_RESOURCE_INTEGRATION_TESTS
    TEST_query = "cow"

    google_key = settings.GOOGLE_API_KEY
    google_cx = '004613812033868156538:5pcwbuudj1m'

    wiki_translate_to = 'pt'
    wiki_excluded_properties = [  # should be wiki namespace!
        'P31',  # instance of
        'P21',  # sex or gender
        'P27',  # country of citizenship
        'P143',  # imported from
        'P248',  # claim stated in
        'P910',  # topic's main category
    ]
    wiki_extracts = False

    translate_media = 'videos,images'  # can't be plural yet

