from invoke import task
from src.datascope.version import get_project_version


REPOSITORY = "eu.gcr.io/datascope-266618"


@task()
def container(ctx, version=None):

    if not version:
        version = get_project_version("src/package.json")

    print(f"Building: {version}")
    tag = f"{REPOSITORY}/datascope:{version}"
    rsl = ctx.run(
        f"docker build . -t {tag}",
        echo=True
    )

    if rsl.failed:
        print(rsl.stderr)
        raise RuntimeError("Failed to build docker image")

    print("Pushing")
    rsl = ctx.run(
        "docker push {}".format(tag),
        echo=True,
        pty=True
    )

    if rsl.failed:
        print(rsl.stderr)
        raise RuntimeError("Failed to push image tagged {}".format(tag))


@task()
def translations(ctx):
    with ctx.cd("src"):
        print("Make messages")
        ctx.run("python manage.py makemessages --all", echo=True)
        print("Compiling local messages")
        ctx.run("python manage.py compilemessages", echo=True)
