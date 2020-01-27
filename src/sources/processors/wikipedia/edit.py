import requests

from core.processors import HttpResourceProcessor

from sources.models import WikipediaToken, WikipediaLogin


class WikipediaEditProcessor(HttpResourceProcessor):

    @classmethod
    def get_session(cls, config):
        session = requests.Session()
        login_token = WikipediaToken(session=session).post("login").get_token()
        WikipediaLogin(session=session, token=login_token).post(
            username=config.username,
            password=config.password
        )
        edit_token = WikipediaToken(session=session).post("csrf").get_token()
        session.token = edit_token
        return session
