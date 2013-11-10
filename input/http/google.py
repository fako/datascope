from HIF.input.http.core import JsonQueryLink
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

    # Class props
    _config = ["query","key","cx"]
    _config_namespace = "google"

    def enable_auth(self):
        super(GoogleImage, self).enable_auth()
        key = self.config.key
        cx = self.config.cx
        self.auth_link += unicode(('&key={}&cx={}'.format(key, cx)))

    def handle_error(self):
        try:
            return super(GoogleImage,self).handle_error()
        except HIFHttpError40X, exception:
            if self.status == 403:
                raise HIFHttpLinkPending(exception.message)
            else:
                raise exception

    class Meta:
        proxy = True