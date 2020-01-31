"""
A file with tasks that can be executed on nodes
This file needs to be compatible with invoke 0.11.0
"""
from getpass import getpass
from datetime import datetime
try:
    from invoke import ctask as task
except ImportError:
    from invoke import task


REPOSITORY = "eu.gcr.io/datascope-266618"


@task()
def init(ctx, mode, role):
    assert role in ["worker", "web", f"Only 'web' and 'worker' are valid roles not {role}"]
    ctx.run(f"cp environments/{mode}/secrets/.env .env")
    ctx.run(f"cp docker-compose.{role}.yml docker-compose.yml")


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
        "docker-compose -f docker-compose.yml down && "
        "docker-compose -f docker-compose.yml up -d",
        # "docker-compose -f docker-compose.yml config 2>/dev/null | "  # compiles configuration
        # "docker stack deploy -c - --with-registry-auth --prune datascope",  # deploys latest "datascope" service
        echo=True,
    )


@task()
def migrate(ctx, version):
    postgres_password = getpass("Postgres password:")
    print("Running migration with root database user through docker-compose run ...")
    ctx.run(
        f"export RELEASE_VERSION={version} && "
        f"export INVOKE_POSTGRES_CREDENTIALS=postgres:{postgres_password} && "
        "docker-compose -f docker-compose.yml run --rm datascope python manage.py migrate"
    )


@task()
def run(ctx, version):
    ctx.run(
        f"export RELEASE_VERSION={version} && "
        "docker-compose -f docker-compose.yml run --rm datascope bash"
    )


@task()
def publish_scripts(ctx):
    ctx.run("rm -f deploy/.env")
    ctx.run("gsutil rsync -rd -J deploy gs://ds-deploy/")


@task()
def update_scripts(ctx):
    ctx.run("gsutil rsync -r -J gs://ds-deploy/ .")


@task()
def prune(ctx):
    ctx.run("docker system prune --all")


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
    ctx.run("psql -h localhost -U postgres -Atq -f reset.sql -o tmp.sql datascope")
    # And then we execute that output
    ctx.run("psql -h localhost -U postgres -f tmp.sql datascope")
    ctx.run("rm tmp.sql")
