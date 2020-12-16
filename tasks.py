from invoke import Collection
from build import container, translations
from deploy.tasks import publish_scripts, db_dump, db_load


namespace = Collection(
    Collection("build", container, translations),
    Collection("deploy", publish_scripts, db_dump, db_load)
)
