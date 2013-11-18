# Settings for HIF come from the Domain class.
# Later it will be easy to load configs out of the db.
class Domain(object):

    HIF__supported_languages = ['en','nl','pt','de','fr','es']
    HIF_debug = True

    google_key = 'AIzaSyDf2Eop-euHJGF1oOalFz3cYYZtQkquU1o'
    google_cx = '004613812033868156538:5pcwbuudj1m'

    wiki_source_language = 'en'
    wiki_translate_to = 'pt'

