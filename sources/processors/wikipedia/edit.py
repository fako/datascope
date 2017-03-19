import requests

from core.processors import HttpResourceProcessor

from sources.models import WikipediaToken, WikipediaLogin


class WikipediaEditProcessor(HttpResourceProcessor):

    def __init__(self, *args, **kwargs):
        super(WikipediaEditProcessor, self).__init__(*args, **kwargs)
        self.session = None

    def get_session(self):
        if self.session and self.config.token:
            return self.session
        session = requests.Session()
        login_token = WikipediaToken(session=session).post("login").get_token()
        WikipediaLogin(session=session, token=login_token).post(
            username=self.config.username,
            password=self.config.password
        )
        edit_token = WikipediaToken(session=session).post("csrf").get_token()
        self.config.token = edit_token
        self.session = session
        return self.session
