"""
A file with tasks that can be executed on nodes
This file needs to be compatible with invoke 0.11.0
"""
from datetime import datetime
from pprint import pprint
from getpass import getpass
try:
    from invoke import ctask as task
except ImportError:
    from invoke import task


REPOSITORY = "eu.gcr.io/datascope-266618"


def get_versions_by_mode(ctx):
    rsl = ctx.run("docker image ls", hide=True)
    versions = {}
    modes = {}
    lines = rsl.stdout.split("\n")
    for line in lines:
        if not line.startswith(REPOSITORY):
            continue
        info = line.split()
        if info[1] in ["prd", "acc"]:
            modes[info[1]] = info[2]
        else:
            versions[info[2]] = info[1]
    return {
        mode: versions[image]
        for mode, image in modes.items()
    }


def get_new_versions(ctx):
    # Get the lastest local version of an image
    local_images = ctx.run("docker image ls", hide=True)
    last_local_image = next(image for image in local_images.stdout.split("\n") if image.startswith(REPOSITORY))
    last_local_version_columns = last_local_image.split()
    last_local_version = last_local_version_columns[1] if len(last_local_version_columns) else None
    # List all versions of the images from the remote
    versions = []
    remote_images = ctx.run(f"gcloud container images list-tags {REPOSITORY}/datascope", hide=True)
    lines = remote_images.stdout.split("\n")
    for line in lines:
        if line.startswith("DIGEST"):
            continue
        info = line.split()
        if len(info) < 3:
            continue
        versions.append(info[1])
    # Find the local version in the versions list and return everything that's newer
    if last_local_version is not None:
        last_local_version_ix = versions.index(last_local_version)
        versions = versions[:last_local_version_ix+1]
    return versions


@task()
def pull(ctx, version=None, latest_only=True):
    if version is None:
        version = get_new_versions(ctx)
    else:
        version = version.split(",")
    if not len(version):
        print("No new images to pull")
        return

    if latest_only:
        version = version[:1]
    print("Pulling:", version)
    for tag in version:
        ctx.run(
            f"docker pull {REPOSITORY}/datascope:{tag}",
            echo=True,
            pty=True
        )


@task()
def list(ctx):
    ctx.run("docker image ls")
    pprint(get_versions_by_mode(ctx))


@task()
def promote(ctx, version, mode="production"):

    # Prepare the update
    mode_to_tag = {
        "production": "prd"
    }
    tag = mode_to_tag.get(mode, None)
    assert tag is not None, f"Did not recognize mode {mode}"
    # Run commands that update the image tags
    ctx.run(
        f"docker rmi {REPOSITORY}/datascope:{tag}",
        echo=True,
        warn=True,
        hide="err"
    )
    ctx.run(
        f"docker tag {REPOSITORY}/datascope:{version} {REPOSITORY}/datascope:{tag}",
        echo=True,
        pty=True
    )


@task()
def init(ctx, mode, role):
    assert role in ["worker", "web", f"Only 'web' and 'worker' are valid roles not {role}"]
    # Setup basic configuration
    ctx.run(f"cp environments/{mode}/secrets/.env .env")
    ctx.run(f"cp docker-compose.{role}.yml docker-compose.yml")
    # Setup images
    versions = get_new_versions(ctx)
    if not len(versions):
        print("No versions found in docker repository")
        return
    promote(ctx, versions[0])


@task()
def deploy(ctx):
    versions = get_versions_by_mode(ctx)
    ctx.run(
        f"RELEASE_VERSION={versions['prd']} "
        "docker-compose -f docker-compose.yml config 2>/dev/null | "  # compiles configuration
        "docker stack deploy -c - --with-registry-auth --prune service ",
        echo=True,
    )


@task()
def migrate(ctx, mode):
    versions = get_versions_by_mode(ctx)
    postgres_password = getpass("Postgres password:")
    print("Running migration with root database user through docker-compose run ...")
    # docker exec $(docker ps -q -f name=service_datascope) python manage.py migrate
    ctx.run(
        f"RELEASE_VERSION={versions['prd']} "
        f"INVOKE_POSTGRES_CREDENTIALS=postgres:{postgres_password} "
        f"docker-compose -f docker-compose.yml run --rm {mode} python manage.py migrate"
    )


@task()
def run(ctx, mode):
    versions = get_versions_by_mode(ctx)
    print(f"Starting a bash shell in a {mode} container through docker-compose run ...")
    ctx.run(
        f"RELEASE_VERSION={versions['prd']} "
        f"docker-compose -f docker-compose.yml run --rm {mode} bash"
    )


@task()
def publish_scripts(ctx):
    ctx.run("gsutil rsync -rd -J deploy gs://ds-deploy/")


@task()
def update_scripts(ctx):
    ctx.run("gsutil rsync -r -J gs://ds-deploy/ .")


@task()
def prune(ctx):
    versions = get_versions_by_mode(ctx)
    ctx.run("docker system prune --all")  # this clears everything also tags!
    # Now we bring back the necessary tags
    for mode, version in versions.items():
        ctx.run(
            f"docker tag {REPOSITORY}/datascope:{mode} {REPOSITORY}/datascope:{version}",
            echo=True,
            pty=True
        )


@task()
def db_dump(ctx):
    now = datetime.now()
    ctx.run(f"pg_dump -h localhost -U postgres datascope > datascope.postgres.{now:%Y-%m-%d}.sql")


@task()
def db_load(ctx, dump_file):
    # First we pipe a dumpfile into psql
    ctx.run(f"cat {dump_file} | psql -h localhost -U postgres datascope")
    # Now we need to reset sequences to make sure that autoid fields act normally
    # For this we store the output of reset.sql into a tmp file
    ctx.run("psql -h localhost -U postgres -Atq -f deploy/reset.sql -o tmp.sql datascope")
    # And then we execute that output
    ctx.run("psql -h localhost -U postgres -f tmp.sql datascope")
    ctx.run("rm tmp.sql")
