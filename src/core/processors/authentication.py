from django.apps import apps

from core.processors import HttpResourceProcessor


class HttpPrivateResourceProcessor(HttpResourceProcessor):
    """
    Establishes a session in order to reach private resources
    """

    @classmethod
    def get_session(cls, config):  # TODO: test to unlock
        auth_config = config.auth
        login_resource = apps.get_model(auth_config["resource"])
        login_credentials = auth_config["credentials"]
        login = login_resource()
        login.post(**login_credentials)
        return login.session
