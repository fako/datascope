import os

from datagrowth import settings as datagrowth_settings


def get_model_path(app_label, model_type=""):
    return os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, app_label, model_type).rstrip(os.sep)


def get_media_path(app_label, media_type="", absolute=True):
    if absolute:
        return os.path.join(datagrowth_settings.DATAGROWTH_MEDIA_ROOT, app_label, media_type).rstrip(os.sep)
    else:
        return os.path.join(app_label, media_type).rstrip(os.sep)


def get_dumps_path(model):
    return os.path.join(datagrowth_settings.DATAGROWTH_DATA_DIR, model._meta.app_label, "dumps", model.get_name())
