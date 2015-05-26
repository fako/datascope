from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import range

from django.core.management.base import BaseCommand

from core.processors.resources import HttpResourceProcessor
from core.processors.extraction import ExtractProcessor
from sources.models.websites.acteursspot import ActeursSpotProfile


class Command(BaseCommand):
    """
    Commands to work with Acteurs Spot website.
    """

    SITE_SIZE = 1700

    def add_arguments(self, parser):
        parser.add_argument('subcommand', type=unicode, choices=['fetch', 'extract'])
        parser.add_argument('-l', '--limit', type=int, nargs="?", default=1)

    def fetch(self, limit=1):
        """
        Scrapes profiles of actors/actresses from Acteurs Spot

        :param limit: limits how much responses should be fetched (0 for unlimited)
        :return: None
        """
        size = limit or self.SITE_SIZE
        args_list = [[i] for i in range(1, size+1)]
        kwargs_list = [{} for i in range(size+1)]
        config = {
            "resource":"ActeursSpotProfile",
            "interval_duration": 1000
        }

        hrp = HttpResourceProcessor(config=config)
        task = hrp.fetch_mass.delay(args_list, kwargs_list)

        return task

    @staticmethod
    def extract(limit=1):
        """
        Will extract data from Acteurs Spot responses that should have been fetched.

        :param limit: limits how much responses need to get extracted (0 for unlimited)
        :return: None
        """
        if not limit:
            limit = ActeursSpotProfile.objects.filter(status=200).count()

        ep = ExtractProcessor(objective={
            "@": "soup.find('html')",
            "achternaam": "el.find('title').text.replace('Profiel van ', '').replace(' | Acteursspot','')",
            "voornaam": "el.find(id='profiel_data_naam').text.strip().split(' ')[0]",
            "afbeelding": "el.find(id='profiel_data_profielfoto').find('img')['src']"
        })
        results = []
        for link in ActeursSpotProfile.objects.filter(status=200)[:limit]:
            content_type, data = link.content
            results += ep.extract(content_type, data)

        return results

    def handle(self, **options):
        execute = getattr(self, options["subcommand"])
        print(execute(limit=options["limit"]))

