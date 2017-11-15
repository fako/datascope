from core.processors import HttpResourceProcessor
from core.utils.helpers import get_any_model


class HttpPrivateResourceProcessor(HttpResourceProcessor):
    """
    Establishes a session in order to reach private resources
    """

    @classmethod
    def get_session(cls, config):  # TODO: test to unlock
        auth_config = config.auth
        login_resource = get_any_model(auth_config["resource"])
        login_credentials = auth_config["credentials"]
        login = login_resource()
        login.post(**login_credentials)
        return login.session
