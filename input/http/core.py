import requests

from HIF.exceptions import HIFHttpError40X, HIFHttpError50X
from HIF.models.storage import TextStorage
from HIF.helpers.mixins import JsonDataMixin


class HttpLink(TextStorage):

    # HIF interface attributes
    HIF_parameters = {}
    HIF_link = ''

    # Class attributes
    request_headers = {}


    def __init__(self, *args, **kwargs):
        super(HttpLink, self).__init__(*args, **kwargs)
        self.refresh = False
        self.prepare = True
        self.session = None
        self._link = ''


    def success(self): # TODO: tests
        """
        Returns True if status is within HTTP success range
        """
        return bool(self.status >= 200 and self.status < 300)

    @property
    def url(self): # TODO: tests
        if not self._link:
            self.prepare_link()
        return self._link


    # Main function.
    # Does a get to computed link
    def get(self, *args, **kwargs):

        self.setup(*args, **kwargs)

        # Early exit if response is already there and status within success range.
        if self.success() and not self.refresh:
            return self
        else:
            self.head = {}
            self.body = ""
            self.status = 0

        # Prepare to do a get if necessary in context
        if self.prepare:
            self.prepare_link()
            self.enable_auth()

        # Make request and do basic response handling
        self.send_request()
        self.store_response()
        self.handle_error()

        return self

    def prepare_link(self):
        """
        Turns _parameters dictionary into valid query string
        Will execute any callables in values of _parameters
        """
        url = self.HIF_link
        if self.HIF_parameters:
            url += u'?'
            for key ,value in self.HIF_parameters.iteritems():
                if callable(value):
                    value = value()
                url += key + u'=' + unicode(value) + u'&'
            url = url[:-1] # strips '&' from the end
        self._link = url

    def enable_auth(self):
        """
        Should do authentication and set auth_link to proper authenticated link.
        """
        self._link = self.url # equal to _link = _link except url fills _link if empty ... make explicit?

    def send_request(self):
        """
        Does a get on the computed link
        Will set storage fields to returned values
        """
        if self.session is None:
            connection = requests
        else:
            connection = self.session
        response = connection.get(self.url, headers=self.request_headers)

        self.head = dict(response.headers)
        self.body = response.content
        self.status = response.status_code

    def store_response(self):
        """
        Stores self if it needs to be cached or the retrieval failed (for debug purposes)
        """
        if not self.success():
            self.save()
            return True
        return False

    def handle_error(self):
        """
        Raises exceptions upon error statuses
        """
        if self.status >= 500:
            message = "{} > {} \n\n {}".format(self.type, self.status, self.body)
            raise HIFHttpError50X(message)
        elif self.status >= 400:
            message = "{} > {} \n\n {}".format(self.type, self.status, self.body)
            raise HIFHttpError40X(message)
        else:
            return True


    class Meta:
        proxy = True


class HttpQueryLink(HttpLink):

    # HIF attributes
    HIF_query_parameter = ''

    def get(self, *args, **kwargs):
        assert len(args) == 1, "HIFImproperUsage: QueryLinks should receive only one args parameter."
        self.HIF_parameters[self.HIF_query_parameter] = args[0]
        super(HttpQueryLink, self).get(*args, **kwargs)

    class Meta:
        proxy = True


class JsonQueryLink(HttpQueryLink, JsonDataMixin):

    request_headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    def __init__(self, *args, **kwargs):
        super(JsonQueryLink, self).__init__(*args, **kwargs)
        JsonDataMixin.__init__(self)

    @property
    def data_source(self):
        """
        This property should return the data that DataMixin's extract should work with
        """
        return self.body

    class Meta:
        proxy = True