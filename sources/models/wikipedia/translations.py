from datagrowth.exceptions import DGHttpError40X
from datagrowth.utils import override_dict

from sources.models.wikipedia.query import WikipediaPage


class WikipediaTranslate(WikipediaPage):

    URI_TEMPLATE = 'http://{}.wiktionary.org/w/api.php?{}={}&iwprefix={}'  # updated at runtime

    PARAMETERS = override_dict(WikipediaPage.PARAMETERS, {
        'prop': 'info|pageprops|iwlinks',
        'iwprop': 'url',
    })

    def variables(self, *args):
        args = args or self.request.get("args")
        variables = super().variables(*args)
        variables.update({
            "term": args[2],
            "language": args[3]
        })
        return variables

    def handle_errors(self):
        super(WikipediaTranslate, self).handle_errors()
        if not "iwlinks" in self.body:
            self.status = 404
            raise DGHttpError40X(
                "No translations found for {term} in {language}".format(**self.variables()),
                resource=self
            )
