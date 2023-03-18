import os
from invoke import Collection, Exit
from fabric import task
import signal

from datascope.configuration import environment


@task(name="shell")
def shell(conn):
    """
    Forwards Postgres ports and starts a Django shell to debug remote data.
    """
    mode = os.environ.get("DJANGO_MODE", None)
    if mode is None or mode == "development":
        raise Exit(f"Did not expect DJANGO_MODE to be '{mode}' for fabric command using logins")

    print(f"Starting Python shell with Django models loaded connected to Google Cloud")
    with conn.forward_local(local_port=9201, remote_port=9200):
        with conn.forward_local(local_port=5433, remote_port=5432):
            conn.local(
                f"INVOKE_ELASTIC_SEARCH_HOST=http://localhost:9201 "
                f"INVOKE_POSTGRES_HOST=localhost "
                f"INVOKE_POSTGRES_PORT=5433 "
                f"python manage.py shell",
                echo=True, pty=True
            )


@task(name="kibana")
def kibana(conn):
    """
    Forwards a port to the Kibana instance. Useful to inspect Elasticsearch.
    """
    print("Kibana dashboard available with SSH encryption at: http://localhost:5602/")
    with conn.forward_local(local_port=5602, remote_port=5601):
        signal.pause()


connect = Collection("connect", shell, kibana)
connect.configure(environment)

namespace = Collection(
    connect
)
