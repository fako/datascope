from HIF.input.http.links import JsonQueryLink
from HIF.models.settings import Domain
from HIF.exceptions import HIFHttpError40X, HIFHttpLinkPending

DOMAIN = Domain()

class GoogleImage(JsonQueryLink):

    # HIF interface
    _link = 'https://www.googleapis.com/customsearch/v1'
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

    def handle_error(self):
        try:
            return super(GoogleImage,self).handle_error()
        except HIFHttpError40X, exception:
            if self.status == 403:
                raise HIFHttpLinkPending(exception.message)
            else:
                raise exception