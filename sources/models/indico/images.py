from __future__ import unicode_literals, absolute_import, print_function, division

import logging
import indicoio

from core.models.resources.http import HttpResource

log = logging.getLogger(__name__)


class ImageFeatures(HttpResource):

    CONFIG_NAMESPACE = "indico"

    def variables(self, *args):
        args = args or self.request.get("args")
        return {
            "image": args[0],
        }

    def _create_request(self, method, *args, **kwargs):
        self._validate_input(method, *args, **kwargs)
        vars = self.variables(*args)
        return self.validate_request({
            "args": args,
            "kwargs": kwargs,
            "method": method,
            "input": vars["image"]
        }, validate_input=False)

    def _send(self):
        """
        Does a get on the computed link
        Will set storage fields to returned values
        """
        assert self.request and isinstance(self.request, dict), \
            "Trying to make request before having a valid request dictionary."

        response = None
        indicoio.config.api_key = self.config.api_key
        try:
            response = indicoio.image_features(self.request["input"])
        except Exception as exc:
            log.exception(exc)
            self.set_error(-1)

        self._update_from_response(response)

    def _update_from_response(self, response):
        vars = self.variables()
        self.head = {}
        self.status = 1
        self.body = {
            "image": vars["image"],
            "vectors": response
        }

    @property
    def success(self):
        return self.status == 1

    @property
    def content(self):
        if self.success:
            return "application/json", self.body
        return None, None
