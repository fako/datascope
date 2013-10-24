from HIF.models import DataLinkMixin
from HIF.input.http.hif import QueryLink
from HIF.processors.extractors import json_extractor
from HIF.exceptions import WaitingForAPIResponse

class GoogleImage(QueryLink, DataLinkMixin):

    # HIF interface
    _link_type = 'GoogleImage'
    _link = 'https://www.googleapis.com/customsearch/v1' # updated at runtime
    _parameters = {
        'searchType':'image',
    }
    _objective = {
        "contextLink": None,
        "thumbnailLink": None,
    }
    _query_parameter = 'q'

    # Class attributes
    key = ''
    cx = ''

    def __init__(self, key='AIzaSyDf2Eop-euHJGF1oOalFz3cYYZtQkquU1o', cx='004613812033868156538:5pcwbuudj1m', *args, **kwargs):
        self.key = key
        self.cx = cx
        super(GoogleImage, self).__init__(*args, **kwargs)

    def enable_auth(self):
        self.auth_link = self.link + unicode(('&key={}&cx={}'.format(self.key, self.cx)))

    def extract_results(self):
        # Extract
        return json_extractor(self.response, self._objective)

    def handle_error(self):
        # Extract and clean error response
        self.errors = json_extractor(self.response, {'code': 600, 'message': 'Unknown Error'})
        def error_cleaner(rsl):
            if "code" in rsl and rsl["code"] == 600: return False
            return True
        self.errors = filter(error_cleaner,self.errors)
        # Handle errors
        for e in self.errors:
            if e['message'] == "Daily Limit Exceeded": raise WaitingForAPIResponse(self._link_type + ': ' + e["message"])
        # If everything went well we simply return
        return True

    def continue_request(self):
        pass