from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import HttpResource
from core.exceptions import DSHttpError40X, DSHttpError403LimitExceeded, DSHttpWarning204


class GoogleQuery(HttpResource):

    CONFIG_NAMESPACE = "google"

    def auth_parameters(self):
        return {
            "key": self.config.api_key
        }

    def _handle_errors(self):
        try:
            no_errors = super(GoogleQuery, self)._handle_errors()
        except DSHttpError40X as exception:
            if self.status == 403:
                raise DSHttpError403LimitExceeded(exception, resource=self)
            else:
                raise exception
        content_type, data = self.content
        if no_errors and "items" not in data:
            self.status = 204
            # TODO: make clear which results are missing through "variables" interface
            raise DSHttpWarning204("Google Search did not yield any results.", resource=self)

    @property
    def success(self):
        return super(GoogleQuery, self).success and self.status != 204

    class Meta:
        abstract = True
