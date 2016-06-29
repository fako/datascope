from __future__ import unicode_literals, absolute_import, print_function, division

import operator
from datetime import datetime

from django.apps import apps as django_apps
from django.conf import settings


def get_any_model(name):
    try:
        app_label, model = next(
            (model._meta.app_label, model.__name__)
            for model in django_apps.get_models() if model.__name__ == name
        )
    except StopIteration:
        raise LookupError("Could not find {} in any app_labels".format(name))
    return django_apps.get_model(app_label, name)


def parse_datetime_string(time_str):
    try:
        return datetime.strptime(time_str, settings.DATASCOPE_DATETIME_FORMAT)
    except ValueError:
        return None


def format_datetime(datetime):
    return datetime.strftime(settings.DATASCOPE_DATETIME_FORMAT)


def override_dict(parent, child):
    assert isinstance(parent, dict), "The parent is not a dictionary."
    assert isinstance(child, dict), "The child is not a dictionary"
    return dict(parent.copy(), **child)


def merge_iter(*iterables, **kwargs):
    """
    Given a set of reversed sorted iterables, yield the next value in merged order
    Takes an optional `key` callable to compare values by.

    Based on: http://stackoverflow.com/questions/14465154/sorting-text-file-by-using-python/14465236#14465236
    """
    key_func = operator.itemgetter(0) if 'key' not in kwargs else lambda item, key=kwargs['key']: key(item[0])
    order_func = min if 'reversed' not in kwargs or not kwargs['reversed'] else max

    iterables = [iter(it) for it in iterables]
    iterables = {i: [next(it), i, it] for i, it in enumerate(iterables)}
    while True:
        value, i, it = order_func(iterables.values(), key=key_func)
        yield value
        try:
            iterables[i][0] = next(it)
        except StopIteration:
            del iterables[i]
            if not iterables:
                raise


# def get_json(model_instance):
#     if self.lazy:
#         state = getattr(model_instance, Creator._state_key, None)
#         if state is None or not state.get(self.attname, False):
#             return model_instance.__dict__[self.attname]
#     return self.get_db_prep_value(getattr(model_instance, self.attname, None), force=True)
# setattr(cls, 'get_%s_json' % self.name, get_json)
