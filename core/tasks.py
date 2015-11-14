from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType

from celery import current_app as app


@app.task(name="core.test_task")
def test_task():
    return "test task has run"


@app.task(name="core.manifest_community")
def manifest_community(community_type_id, community_id):
    community_type = ContentType.objects.get(id=community_type_id)
    community = community_type.get_object_for_this_type(id=community_id)
    return community.manifestation
