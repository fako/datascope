from __future__ import unicode_literals, absolute_import, print_function, division
import six

from copy import copy


class ExtractProcessor(object):

    def __init__(self, objective):
        super(ExtractProcessor, self).__init__()
        self._at = None
        self._context = {}
        self._objective = {}
        self.load_objective(objective)

    def load_objective(self, objective):
        for key, value in six.iteritems(objective):
            if key == "@":
                self._at = value
            elif key.startswith("#"):
                self._context.update({key[1:]: value})
            else:
                self._objective.update({key: value})
        assert self._at, \
            "ExtractProcessor did not load elements to start with from its objective {}. " \
            "Make sure that '@' is specified".format(objective)
        assert self._objective, "No objectives loaded from objective {}".format(objective)

    def extract(self, content_type, data):
        content_type_method = content_type.replace("/", "_")
        method = getattr(self, content_type_method, None)
        if method is not None:
            return method(data)
        else:
            raise TypeError("Extract processor does not support content_type {}".format(content_type))

    def application_json(self, data):
        pass

    def text_html(self, soup):  # soup used in eval!

        context = {}
        for name, objective in six.iteritems(self._context):
            context[name] = eval(objective)

        at = elements = eval(self._at)
        if not isinstance(at, list):
            elements = [at]

        results = []
        for el in elements:  # el used in eval!
            result = copy(context)
            for name, objective in six.iteritems(self._objective):
                result[name] = eval(objective)
            results.append(result)

        return results
