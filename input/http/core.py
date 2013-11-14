import json, requests

from HIF.exceptions import HIFCouldNotLoadFromStorage, HIFHttpError40X, HIFHttpError50X
from HIF.models.storage import HttpStorage
from HIF.helpers.mixins import JsonDataMixin


class HttpLink(HttpStorage):

    # Class attributes
    auth_link = '' # TODO: rename to URL or something similar
    cache = False
    request_headers = {}
    setup = True

    # HIF interface attributes
    _parameters = {}
    _link = ''

    # Interface

    def success(self): # TODO: tests
        """
        Returns True if status is within HTTP success range
        """
        return bool(self.status >= 200 and self.status < 300)

    @property
    def url(self): # TODO: tests
        if not self._url:
            self.prepare_link()
        return self._url

    # Main function.
    # Does a get to computed link
    def get(self, refresh=False, *args):

        # Early exit if response is already there and status within success range.
        if self.success() and not refresh:
            return self
        else:
            self.head = ""
            self.body = ""
            self.status = 0

        # Prepare to do a get if necessary in context
        if self.setup:
            self.prepare_link()
            self.enable_auth()
            self.identifier = self.identity(self.auth_link)

        # Try a load from database just before making request
        try:
            self.load()
            if self.success(): # early return when previously fetched with success
                print "Returning link from storage"
                return self
        except HIFCouldNotLoadFromStorage:
            pass

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
        url = self._link
        if self._parameters:
            url += u'?'
            for key ,value in self._parameters.iteritems():
                if callable(value):
                    value = value()
                url += key + u'=' + unicode(value) + u'&'
            url = url[:-1] # strips '&' from the end
        self._url = url

    def enable_auth(self):
        """
        Should do authentication and set auth_link to proper authenticated link.
        """
        self.auth_link = self.url

    def send_request(self):
        """
        Does a get on the computed link
        Will set storage fields to returned values
        """
        print "Doing request"
        response = requests.get(self.auth_link, headers=self.request_headers)
        self.head = json.dumps(dict(response.headers), indent=4)
        self.body = response.content
        self.status = response.status_code

    def store_response(self):
        """
        Stores self if it needs to be cached or the retrieval failed (for debug purposes)
        """
        if self.cache or not self.success():
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
    _query_parameter = ''

    def get(self, *args):
        print args
        assert len(args) == 1, "Improper usage: QueryLinks should receive only one args parameter."
        self._parameters[self._query_parameter] = args[0]
        super(HttpQueryLink, self).get()

    class Meta:
        proxy = True


class JsonQueryLink(HttpQueryLink, JsonDataMixin):

    request_headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    @property
    def source(self):
        """
        This property should return the data that DataMixin's extract should work with
        """
        return self.body

    class Meta:
        proxy = True