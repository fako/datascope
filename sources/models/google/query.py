from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import HttpResource
from core.exceptions import DSHttpError40X, DSHttpError403LimitExceeded


class GoogleQuery(HttpResource):

    GOOGLE_QUERY_PARAM = "q"
    CONFIG_NAMESPACE = "google"

    def auth_parameters(self):
        return {
            "key": self.config.api_key
        }

    def _handle_errors(self):
        try:
            return super(GoogleQuery, self)._handle_errors()
        except DSHttpError40X, exception:
            if self.status == 403:
                raise DSHttpError403LimitExceeded(exception, resource=self)
            else:
                raise exception

    def send(self, method, *args, **kwargs):
        args = (self.GOOGLE_QUERY_PARAM,) + args
        return super(GoogleQuery, self).send(method, *args, **kwargs)

    class Meta:
        abstract = True
