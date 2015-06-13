"""
WSGI config for datascope project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
from datascope.settings.setup import SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)

from django.core.wsgi import get_wsgi_application
application = app = get_wsgi_application()  # named app for Wikipedia Labs purposes.
