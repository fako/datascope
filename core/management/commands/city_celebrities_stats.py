import json

from django.core.management.base import BaseCommand

from core.helpers.storage import get_hif_model
from core.helpers.enums import ProcessStatus


class Command(BaseCommand):
    """
    Clears TextStorage and/or ProcessStorage from the database.
    """

    def handle(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        self.args = "<city_name>/<lat>|<lon> <city_name>/<lat>|<lon> ..."

        # Import models here to prevent circular imports
        from core.processes.places import CityCelebrities
        from core.processes.base import Retrieve
        from core.output.http.services.manifests import CityCelebritiesService


        if not args:
            print("You'll need to specify coordinates like: London/51.5286416|-0.1015987")
            return

        for arg in args:

            interesting_claims = [
                {
                    "property": "P106",
                    "item": 33999  # actor
                },
                {
                    "property": "P106",
                    "item": 177220  # singer
                },
                {
                    "property": "P106",
                    "item": 488205  # singer-song writer
                },
                {
                    "property": "P106",
                    "item": 483501  # artist
                },
                {
                    "property": "P106",
                    "item": 2066131  # sports person
                },
                {
                    "property": "P106",
                    "item": 11513337  # athlete competitor
                },
                {
                    "property": "P106",
                    "item": 10800557  # film actor
                },

            ]



            # Start the process
            city, coords = arg.split('/')
            print("Fetching information for: {} at {}".format(city, coords))
            city_celebrities = CityCelebritiesService()
            city_celebrities.setup(query=unicode(city))

            interesting_locations = []
            for location in city_celebrities.content:

                interesting_persons = []
                for person in location['people']:

                    for interesting_claim in interesting_claims:
                        if interesting_claim in person['claims']:
                            interesting_persons.append(person)
                            break

                if len(interesting_persons):
                    location['people'] = interesting_persons
                    interesting_locations.append(location)

            for location in interesting_locations:
                print location['title'], ' > ', len(location['people'])
                print [person['title'] for person in location['people']]
                print
