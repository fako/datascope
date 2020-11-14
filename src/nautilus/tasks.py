import os

from django.core.management import call_command
from celery import current_app as app

from datagrowth.utils import get_media_path
from nautilus.models import LocaforaOrderOverviewCommunity


@app.task(name="nautilus.grow_locafora")
def grow_locafora():
    call_command("grow_locafora")


@app.task(name="nautilus.clear_locafora")
def clear_locafora():
    for entry in os.scandir(get_media_path("nautilus", "locafora")):
        if entry.is_file():
            os.remove(entry.path)
    LocaforaOrderOverviewCommunity.objects.all().delete()
