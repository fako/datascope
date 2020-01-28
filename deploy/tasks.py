"""
A file with tasks that can be executed on nodes
This file needs to be compatible with invoke 0.11.0
"""
from getpass import getpass
try:
    from invoke import ctask as task
except ImportError:
    from invoke import task


REPOSITORY = "eu.gcr.io/good-fashion-friend"


@task()
def pull(ctx, version):
    ctx.run(
        f"docker pull {REPOSITORY}/datascope:{version}",
        echo=True,
        pty=True
    )


@task()
def deploy(ctx, version, debug=False):
    ctx.run(
        ("export INVOKE_DJANGO_DEBUG=1 && " if debug else "") +
        f"export RELEASE_VERSION={version} && "
        "docker-compose -f docker-compose.yml config 2>/dev/null | "  # compiles configuration
        "docker stack deploy -c - --with-registry-auth --prune service",  # deploys latest "service"
        echo=True,
    )


@task()
def migrate(ctx, version):
    postgres_password = getpass("Postgres password:")
    print("Running migration with root database user through docker-compose run ...")
    ctx.run(
        f"export RELEASE_VERSION={version} && "
        f"export INVOKE_POSTGRES_CREDENTIALS=postgres:{postgres_password} && "
        "docker-compose -f docker-compose.yml run --rm service python manage.py migrate"
    )


@task()
def publish_scripts(ctx):
    ctx.run("gsutil rsync -rd -J deploy gs://gff-deploy/")


@task()
def prune(ctx):
    ctx.run("docker system prune --all")
