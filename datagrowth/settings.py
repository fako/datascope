import os

from django.conf import settings


DATAGROWTH_DATETIME_FORMAT = getattr(settings, "DATAGROWTH_DATETIME_FORMAT", "%Y%m%d%H%M%S%f")

DATAGROWTH_DATA_DIR = getattr(settings, "DATAGROWTH_DATA_DIR", os.path.join(settings.BASE_DIR, "data"))
DATAGROWTH_MEDIA_ROOT = getattr(settings, "DATAGROWTH_MEDIA_ROOT", settings.MEDIA_ROOT)
DATAGROWTH_BIN_DIR = getattr(settings, "DATAGROWTH_BIN_DIR",
    os.path.join(settings.BASE_DIR, "datagrowth", "resources", "shell", "bin")
)

DATAGROWTH_REQUESTS_PROXIES = getattr(settings, "DATAGROWTH_REQUESTS_PROXIES", None)
DATAGROWTH_REQUESTS_VERIFY = getattr(settings, "DATAGROWTH_REQUESTS_VERIFY", True)
