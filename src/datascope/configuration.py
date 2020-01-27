"""
This module exposes the environment which is an invoke Config that holds environment specific configuration.
The idea is that all configuration is managed by just two environment variables:
 * DJANGO_MODE
 * DJANGO_CONTEXT
The first specifies a mode like "production", "acceptance" or "development".
The latter specifies how the configuration files are found. Inside a Docker container or outside of them.
Read more about invoke Config here: http://docs.pyinvoke.org/en/stable/concepts/configuration.html#config-hierarchy

Since the config is created outside of invoke there are a few special adjustments
The system invoke files are the environment configuration files.
While the user invoke files are the secret configuration files.
For the rest the project and shell environment variables get loaded as normal and my override environments and secrets.
"""
import os
from invoke.config import Config
from datascope.version import get_project_version


MODE = os.environ.get("DJANGO_MODE", "production")
CONTEXT = os.environ.get("DJANGO_CONTEXT", "container")

BASE_ENVIRONMENT = "/usr/etc/datascope" if CONTEXT == "container" else "../deploy/environments"
MODE_ENVIRONMENT = os.path.join(BASE_ENVIRONMENT, MODE)
SECRET_ENVIRONMENT = os.path.join(MODE_ENVIRONMENT, "secrets")


environment = Config(
    overrides={
        "project_version": get_project_version("package.json")
    },
    system_prefix=MODE_ENVIRONMENT + os.path.sep,
    user_prefix=SECRET_ENVIRONMENT + os.path.sep
)
environment.load_system()
environment.load_user()
environment.load_project()
environment.load_shell_env()

# Load computed overrides (we post process to prevent setting some variables everywhere)
database_credentials = environment.postgres.credentials
if database_credentials:
    user, password = database_credentials.split(":")
    environment.load_overrides({
        "project_version": get_project_version("package.json"),
        "django": {
            "database_user": user,
            "database_password": password
        }
    })
