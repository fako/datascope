from __future__ import unicode_literals, absolute_import, print_function, division

from jsonpath_rw import parse as jsonpath_parse

from django.apps import apps as django_apps


def get_any_model(name):
    try:
        app_label, model = next(
            (model._meta.app_label, model.__name__)
            for model in django_apps.get_models() if model.__name__ == name
        )
    except StopIteration:
        raise LookupError("Could not find {} in any app_labels".format(name))
    return django_apps.get_model(app_label, name)


def override_dict(parent, child):
    assert isinstance(parent, dict), "The parent is not a dictionary."
    assert isinstance(child, dict), "The child is not a dictionary"
    return dict(parent.copy(), **child)


def reach(json_path, data):
    expr = jsonpath_parse(json_path)
    try:
        return expr.find(data)[0].value
    except IndexError:
        return None