import httplib2

from HIF.models import DataLink, DataLinkMixin


class HTTPLink(DataLink, DataLinkMixin):

    _parameters = {}

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
        super(HTTPLink, self).send_request() # may fetch cache result by throwing CacheResult

        print "HTTPLink.send_request is being executed."
        connection = httplib2.Http()
        meta, content = connection.request(self.auth_link)
        self.response = content


class QueryLink(HTTPLink):

    _query_parameter = ''
    _query = ''

    def get(self, query, refresh=False, *args, **kwargs):
        if isinstance(query,list):
            #TODO: make multi term queries work
            for q in query:
                self._query = q # included through prepare_link()
                super(QueryLink, self).get(*args, **kwargs)
        else:
            self._query = query # included through prepare_link()
            super(QueryLink, self).get(*args, **kwargs)



        return iter(self.results)

    def prepare_link(self, *args, **kwargs):
        self._parameters[self._query_parameter] = self._query
        super(QueryLink, self).prepare_link(*args, **kwargs)

