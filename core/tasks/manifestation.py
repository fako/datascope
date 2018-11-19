import logging

from celery import current_app as app

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.resources.manifestation import Manifestation
from core.views import CommunityView
from core.utils.configuration import load_config
from core.utils.helpers import get_any_model


log = logging.getLogger("datascope")


@app.task(name="core.get_manifestation_data")
def get_manifestation_data(manifestation_id):
    manifestation = Manifestation.objects.get(id=manifestation_id)
    community = manifestation.community
    community.config = manifestation.config
    return list(community.manifestation)


@app.task(name="core.manifest")
@load_config(defaults=DEFAULT_CONFIGURATION)
def manifest(config, *args, **kwargs):
    success = []
    errors = []
    community_model = get_any_model(config.community)
    signature = community_model.get_signature_from_input(*args, **kwargs)
    try:
        community_instance = community_model.objects.get_latest_by_signature(signature, **kwargs)
    except community_model.DoesNotExist:
        # We can't manifest without a community, so no results effectively
        # But something should not have been calling this task probably
        log.warning("Community of class {} does not have instance with signature {}".format(
            community_model.__class__.__name__,
            signature
        ))
        return [success, errors]
    growth_configuration = community_model.filter_growth_configuration(**kwargs)
    scope_configuration = community_model.filter_scope_configuration(**kwargs)
    configuration = dict(**growth_configuration)
    configuration.update(**scope_configuration)
    uri = CommunityView.get_uri(community_model, "/".join(args), configuration)
    try:
        manifestation = Manifestation.objects.get(uri=uri)
    except Manifestation.DoesNotExist:
        manifestation = Manifestation(
            uri=uri,
            community=community_instance,
            config=community_model.filter_scope_configuration(*args, **kwargs)
        )
        manifestation.save()
    try:
        manifestation.get_data()
        success.append(manifestation.id)
    except Exception as exc:
        log.error("{}".format(exc))
        errors.append(manifestation.id)
    return [success, errors]


@app.task(name="core.manifest_serie")
@load_config(defaults=DEFAULT_CONFIGURATION)
def manifest_serie(config, args_list, kwargs_list):
    success = []
    errors = []
    for args, kwargs in zip(args_list, kwargs_list):
        scc, err = manifest(config=config, *args, **kwargs)
        success += scc
        errors += err
    return [success, errors]
