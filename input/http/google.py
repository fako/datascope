from HIF.input.http.core import JsonQueryLink
from HIF.models.settings import Domain
from HIF.exceptions import HIFHttpError40X, HIFHttpLinkPending

DOMAIN = Domain()

class GoogleImage(JsonQueryLink):

    # HIF interface
    HIF_link = 'https://www.googleapis.com/customsearch/v1'
    HIF_parameters = {
        'searchType':'image',
    }
    HIF_objective = {
        "contextLink": None,
        "thumbnailLink": None,
    }
    HIF_query_parameter = 'q'

    # Class props
    HIF_namespace = "google"

    def enable_auth(self):
        super(GoogleImage, self).enable_auth()
        key = self.config.key
        cx = self.config.cx
        self._link = self.url + unicode(('&key={}&cx={}'.format(key, cx)))

    def handle_error(self):
        try:
            return super(GoogleImage,self).handle_error()
        except HIFHttpError40X, exception:
            if self.status == 403:
                raise HIFHttpLinkPending(exception.message)
            else:
                raise exception

    class Meta:
        abstract = True