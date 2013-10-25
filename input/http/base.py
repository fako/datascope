import requests

from HIF.models import DataLink, DataLinkMixin
from HIF.exceptions import HIFHTTPError50X, HIFHTTPError40X


class HTTPLink(DataLink, DataLinkMixin):

    # HIF interface vars
    _parameters = {}
    _headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    # Adding parameters on prepare link
    def prepare_link(self):
        self.link = self._link
        if self._parameters:
            self.link += u'?'
            for k,v in self._parameters.iteritems():
                if callable(v):
                    v = v()
                self.link += k + u'=' + unicode(v) + u'&'
            self.link = self.link[:-1] # strips '&' from the end

    # Make connection and do request
    def send_request(self):
        super(HTTPLink, self).send_request() # may fetch cache result by throwing DbResponse
        response = requests.get(self.auth_link,headers=self._headers)
        self.response = response.content
        self.response_status = response.status_code

    # When getting an error message
    # This function expects to get a dict
    def handle_error(self):
        if self.response_status >= 500:
            message = "{} > {} \n\n {}".format(self._link_type, self.response_status,self.response)
            raise HIFHTTPError50X(message)
        elif self.response_status >= 400:
            message = "{} > {} \n\n {}".format(self._link_type, self.response_status,self.response)
            raise HIFHTTPError40X(message)
        else:
            return True


class QueryLink(HTTPLink):

    _query_parameter = ''
    _query = 'test'

    def get(self, query, refresh=False, *args, **kwargs):
        self._query = query # included through prepare_link()
        super(QueryLink, self).get(*args, **kwargs)
        return self.results

    def prepare_link(self, *args, **kwargs):
        self._parameters[self._query_parameter] = self._query
        super(QueryLink, self).prepare_link(*args, **kwargs)

