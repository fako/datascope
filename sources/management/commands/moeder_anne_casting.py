from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves import range

from copy import copy

from pandas import DataFrame

from django.core.management.base import BaseCommand

from core.processors.resources import HttpResourceProcessor
from core.processors.extraction import ExtractProcessor
from sources.models.websites.moederannecasting import MoederAnneCastingSearch
from sources.management.commands.benf_casting import Command as BenfCastingCommand


class Command(BaseCommand):
    """
    Commands to work with Moeder Anne Casting website.
    """

    SITE_SIZE = 620
    BAN = [(u'Marco', u'10-10-2003'), (u'Jaap', u'10-12-1938'), (u'Klaas', u'10-12-1947'), (u'Nico', u'10-12-1962'), (u'Tamara', u'11-12-1981'), (u'Tim', u'11-12-1994'), (u'Rita', u'12-12-1937'), (u'Fleur', u'13-11-1994'), (u'Henny', u'14-10-1937'), (u'Marcello', u'14-11-1947'), (u'Frank', u'15-12-1959'), (u'Wim', u'16-11-1964'), (u'Fatima', u'17-10-1970'), (u'Henk', u'17-12-1952'), (u'Ruud', u'18-11-1939'), (u'Claire', u'19-11-1997'), (u'Bep', u'20-11-1961'), (u'Amarilla', u'21-10-1982'), (u'Rose ', u'23-11-1988'), (u'Marielle', u'24-11-1993'), (u'Kaj', u'26-12-1992'), (u'Rob', u'27-11-1941'), (u'Blanka', u'29-11-1953'), (u'Liset', u'29-12-1983'), (u'Jeffrey', u'30-10-1992'), (u'Anneke', u'30-11-1956')]

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

        return "TASK: {}".format(task)

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

        return Command.filter_by_benf_casting(formatted, BenfCastingCommand.extract(limit))

    def handle(self, **options):
        execute = getattr(self, options["subcommand"])
        print(execute(limit=options["limit"]))

    @staticmethod
    def filter_by_benf_casting(moeder_formatted, benf_formatted):
        df_moeder = DataFrame.from_records(moeder_formatted)
        dfg_moeder = df_moeder.groupby("geboortedatum")
        df_benf = DataFrame.from_records(benf_formatted)
        dfg_benf = df_benf.groupby("geboortedatum")
        benf_birth_dates = dfg_benf.indices

        doubles = []
        for key, details in dfg_moeder:
            if key in benf_birth_dates:
                frames = dfg_benf.get_group(key)
                for ind, rec in details.iterrows():
                    if rec["voornaam"] in frames["voornaam"].values:
                        doubles.append((rec["voornaam"], rec["geboortedatum"],))

        filtered = []
        for data in moeder_formatted:
            if (data["voornaam"], data["geboortedatum"],) not in doubles:
                filtered.append(data)

        return filtered
