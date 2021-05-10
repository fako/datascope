import logging

from celery import current_app as app

from core.models.resources.manifestation import Manifestation


log = logging.getLogger("datascope")


@app.task(name="core.get_manifestation_data")
def get_manifestation_data(manifestation_id):
    manifestation = Manifestation.objects.get(id=manifestation_id)
    community = manifestation.community
    community.config = manifestation.config
    return list(community.manifestation)
