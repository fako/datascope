from __future__ import unicode_literals, absolute_import, print_function, division

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


# def get_json(model_instance):
#     if self.lazy:
#         state = getattr(model_instance, Creator._state_key, None)
#         if state is None or not state.get(self.attname, False):
#             return model_instance.__dict__[self.attname]
#     return self.get_db_prep_value(getattr(model_instance, self.attname, None), force=True)
# setattr(cls, 'get_%s_json' % self.name, get_json)
