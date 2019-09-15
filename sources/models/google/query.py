from datagrowth.resources import HttpResource
from datagrowth.exceptions import DGHttpError40X, DGHttpError403LimitExceeded, DGHttpWarning204


class GoogleQuery(HttpResource):

    CONFIG_NAMESPACE = "google"

    def auth_parameters(self):
        return {
            "key": self.config.api_key
        }

    def _handle_errors(self):
        try:
            no_errors = super(GoogleQuery, self)._handle_errors()
        except DGHttpError40X as exception:
            if self.status == 403:
                raise DGHttpError403LimitExceeded(exception, resource=self)
            else:
                raise exception
        content_type, data = self.content
        if no_errors and "items" not in data:
            self.status = 204
            # TODO: make clear which results are missing through "variables" interface
            raise DGHttpWarning204("Google Search did not yield any results.", resource=self)

    @property
    def success(self):
        return super(GoogleQuery, self).success and self.status != 204

    class Meta:
        abstract = True
