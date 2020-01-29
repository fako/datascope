from invoke import Collection
from build import container
from deploy.tasks import publish_scripts


namespace = Collection(
    Collection("build", container),
    Collection("deploy", publish_scripts)
)
