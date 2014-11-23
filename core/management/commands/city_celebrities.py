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
        self.args = "<city_name>/<lat>|<lon>/<radius> <city_name>/<lat>|<lon>/<radius> ..."

        # Import models here to prevent circular imports
        from core.processes.places import CityCelebrities
        from core.processes.base import Retrieve
        from core.output.http.services.manifests import CityCelebritiesService


        if not args:
            print("You'll need to specify coordinates like: London/51.5286416|-0.1015987/10000")
            return

        for arg in args:

            # Start the process
            city, coords, radius = arg.split('/')
            print("Fetching information for: {} at {} in a radius of {}".format(city, coords, radius))
            city_celebrities = CityCelebrities()
            city_celebrities.execute(coords=coords, radius=radius)

            # Finish the process synchronously
            city_celebrities.task.get()
            city_celebrities.execute(coords=coords)

            if city_celebrities.status != ProcessStatus.DONE:
                print("City Celebrities process failed with: {}".format(city_celebrities.status))
                return

            print("Saving result in service")

            cc_service = CityCelebritiesService()
            cc_service.setup(query=city)
            cc_service.status = 200
            cc_service.content = city_celebrities.rsl
            cc_service.retain()

            print("Printing stats for City Celebrities {}".format(city))

            for location in cc_service.content:
                print location['title'], ' > ', len(location['people'])
                print
                print [person['title'] for person in location['people']]
                print
                print
                print
