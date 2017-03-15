from celery import current_app as app


@app.task(name="core.test_task")
def test_task():
    return "test task has run"


@app.task(name="core.manifest_community")
def manifest_community(manifestation_id):
    from core.models import Manifestation
    manifestation = Manifestation.objects.get(id=manifestation_id)
    community = manifestation.community
    community.config = manifestation.config
    return list(community.manifestation)
