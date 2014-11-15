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

            # Start the process
            city, coords = arg.split('/')
            print("Fetching information for: {} at {}".format(city, coords))
            city_celebrities = CityCelebritiesService()
            city_celebrities.setup(query=unicode(city))

            for location in city_celebrities.content:
                print location['title'], ' > ', len(location['people'])
                print [person['title'] for person in location['people']]
                print ''
