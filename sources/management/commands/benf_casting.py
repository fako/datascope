from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import range

from copy import copy

from pandas import DataFrame

from django.core.management.base import BaseCommand

from core.processors.resources import HttpResourceProcessor
from core.processors.extraction import ExtractProcessor
from sources.models.websites.benfcasting import BenfCastingProfile


class Command(BaseCommand):
    """
    Commands to work with BenF Casting website.
    """

    SITE_SIZE = 19000

    def add_arguments(self, parser):
        parser.add_argument('subcommand', type=unicode, choices=['fetch', 'extract'])
        parser.add_argument('-l', '--limit', type=int, nargs="?", default=1)

    def fetch(self, limit=1):
        """
        Scrapes profiles of actors/actresses from BenF Casting

        :param limit: limits how much responses should be fetched (0 for unlimited)
        :return: None
        """
        size = limit or self.SITE_SIZE
        args_list = [[i] for i in range(1, size+1)]
        kwargs_list = [{} for i in range(size+1)]
        config = {
            "resource": "BenfCastingProfile"
        }

        hrp = HttpResourceProcessor(config=config)
        task = hrp.fetch_mass.delay(args_list, kwargs_list)

        print("TASK:", task)

    @staticmethod
    def extract(limit=1):
        """
        Will extract data from BenF Casting responses that should have been fetched.

        :param limit: limits how much responses need to get extracted (0 for unlimited)
        :return: None
        """
        if not limit:
            limit = BenfCastingProfile.objects.filter(status=200).count()

        ep = ExtractProcessor(objective={
            "@": "soup.find('html')",
            "url": "'http://www.benfcasting.nl/mods/models/index.php?p=viewModel&i=' + el.find_all(class_='detailCell')[0].text",
            "voornaam": "el.find_all(class_='detailCell')[1].text",
            "tussenvoegsel": "el.find_all(class_='detailCell')[2].text",
            "achternaam": "el.find_all(class_='detailCell')[3].text",
            "geboortedatum": "el.find_all(class_='detailCell')[4].text",
            "afbeelding": "'http://www.benfcasting.nl/mods/models/' + el.select('th img')[0]['src'] if el.select('th img') else ''",
        })
        results = []
        for link in BenfCastingProfile.objects.filter(status=200)[:limit]:
            content_type, data = link.content
            results += ep.extract(content_type, data)

        formatted = []
        for rsl in results:
            frsl = copy(rsl)
            year, month, day = rsl["geboortedatum"].split('-')
            frsl["geboortedatum"] = "-".join([day, month, year])
            frsl["achternaam"] = "{} {}".format(rsl["tussenvoegsel"], rsl["achternaam"]) if rsl["tussenvoegsel"] else rsl["achternaam"]
            del frsl["tussenvoegsel"]
            formatted.append(frsl)

        print(formatted)

        df = DataFrame.from_records(formatted)
        df.to_csv("benf_casting.csv")

    def handle(self, **options):
        execute = getattr(self, options["subcommand"])
        execute(limit=options["limit"])

