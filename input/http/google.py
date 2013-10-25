from HIF.models import DataLinkMixin
from HIF.input.http.base import QueryLink
from HIF.processors.extractors import json_extractor
from HIF.exceptions import HIFHTTPError40X, HIFDataLinkPending
from HIF.models.settings import Domain

DOMAIN = Domain()

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

    def __init__(self, key=DOMAIN.google_key, cx=DOMAIN.google_cx, *args, **kwargs):
        self.key = key
        self.cx = cx
        super(GoogleImage, self).__init__(*args, **kwargs)

    def enable_auth(self):
        self.auth_link = self.link + unicode(('&key={}&cx={}'.format(self.key, self.cx)))

    def extract_results(self):
        # Extract
        return json_extractor(self.response, self._objective)

    def handle_error(self):
        try:
            return super(GoogleImage,self).handle_error()
        except HIFHTTPError40X, exception:
            if self.response_status == 403:
                raise HIFDataLinkPending(exception.message)
            else:
                raise exception

    def continue_request(self):
        pass