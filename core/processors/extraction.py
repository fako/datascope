from __future__ import unicode_literals, absolute_import, print_function, division
import six

from copy import copy

from jsonpath_rw import parse as jsonpath_parse


class ExtractProcessor(object):

    def __init__(self, objective):
        super(ExtractProcessor, self).__init__()
        self._at = None
        self._context = {}
        self._objective = {}
        self.load_objective(objective)

    def load_objective(self, objective):
        assert isinstance(objective, dict), "An objective should be a dict."
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

        context = {}
        for name, objective in six.iteritems(self._context):
            context_expr = jsonpath_parse(objective)
            context[name] = context_expr.find(data)[0].value

        at_expr = jsonpath_parse(self._at)
        #nodes = next(match.value for match in at_expr.find(data))
        nodes = at_expr.find(data)[0].value

        results = []
        for node in nodes:
            result = copy(context)
            for name, objective in six.iteritems(self._objective):
                obj_expr = jsonpath_parse(objective)
                result[name] = obj_expr.find(node)[0].value
            results.append(result)

        return results

    def text_html(self, soup):  # soup used in eval!

        context = {}
        for name, objective in six.iteritems(self._context):
            context[name] = eval(objective) if objective else objective

        at = elements = eval(self._at)
        if not isinstance(at, list):
            elements = [at]

        results = []
        for el in elements:  # el used in eval!
            result = copy(context)
            for name, objective in six.iteritems(self._objective):
                result[name] = eval(objective) if objective else objective
            results.append(result)

        return results
