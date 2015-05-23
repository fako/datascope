from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import range

from copy import copy

from django.core.management.base import BaseCommand

from core.processors.resources import HttpResourceProcessor
from core.processors.extraction import ExtractProcessor
from sources.models.websites.moederannecasting import MoederAnneCastingSearch


class Command(BaseCommand):
    """
    Commands to work with Moeder Anne Casting website.
    """

    SITE_SIZE = 620

    def add_arguments(self, parser):
        parser.add_argument('subcommand', type=unicode, choices=['fetch', 'extract'])
        parser.add_argument('-l', '--limit', type=int, nargs="?", default=1)

    def fetch(self, limit=1):
        """
        Scrapes profiles of actors/actresses from Moeder Maria Casting

        :param limit: limits how much responses should be fetched (0 for unlimited)
        :return: None
        """
        size = limit or self.SITE_SIZE
        args_list = [[] for i in range(size)]
        kwargs_list = [{"page": i+1} for i in range(size)]
        config = {
            "resource":"MoederAnneCastingSearch",
            "interval_duration": 1000
        }

        hrp = HttpResourceProcessor(config=config)
        task = hrp.submit_mass.delay(args_list, kwargs_list)

        print("TASK:", task)

    @staticmethod
    def extract(limit=1):
        """
        Will extract data from MoederMariaCastingSearch responses that should have been fetched.

        :param limit: limits how much responses need to get extracted (0 for unlimited)
        :return: None
        """
        if not limit:
            limit = MoederAnneCastingSearch.objects.all().count()

        ep = ExtractProcessor(objective={
            "@": "soup.find_all(class_='record') + soup.find_all(class_='record_alt')",
            "voornaam": "el.select('b:nth-of-type(2)')[0].text.replace('Voornaam: ', '').lower().capitalize()",
            "geboortedatum": "el.select('br:nth-of-type(3)')[0].next_sibling.replace('Geboortedatum: ','')",
            "afbeelding": "el.find('img')['src'] if el.find('img') else ''"
        })
        results = []
        for link in MoederAnneCastingSearch.objects.all()[:limit]:
            content_type, data = link.content
            results += ep.extract(content_type, data)

        formatted = []
        for rsl in results:
            frsl = copy(rsl)
            frsl["geboortedatum"] = rsl["geboortedatum"].replace('/', '-')
            formatted.append(frsl)

        print(formatted)

    def handle(self, **options):
        execute = getattr(self, options["subcommand"])
        execute(limit=options["limit"])

