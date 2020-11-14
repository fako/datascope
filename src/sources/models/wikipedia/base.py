from time import sleep

from core.models.resources.http import HttpResource


class WikipediaAPI(HttpResource):

    CONFIG_NAMESPACE = 'wikipedia'

    HEADERS = {
        "Content-Type": "application/json; charset=utf-8"
    }

    PARAMETERS = {
        "maxlag": "5",
        "format": "json",
        "continue": ""
    }

    ERROR_CODE_TO_STATUS = {
        "no-such-entity": 404,
        "maxlag": 503
    }

    class Meta:
        abstract = True

    def handle_errors(self):
        """
        You can only handle error messages by parsing the body :(
        Include more error codes to translate between Wikipedia and the REST(oftheworld)
        """
        content_type, data = super(WikipediaAPI, self).content
        # This translates between errors in the body and HTTP status
        if data is not None and "error" in data:
            error_code = data["error"]["code"]
            self.set_error(self.ERROR_CODE_TO_STATUS[error_code])
        # Here we act on specific errors that need handling
        if self.status == self.ERROR_CODE_TO_STATUS["maxlag"]:
            maxlag_interval = int(self.head.get("Retry-After", 5))
            sleep(maxlag_interval)
        # HttpResource will now raise exceptions
        super(WikipediaAPI, self).handle_errors()
