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
        from core.output.http.services.manifests import CityCelebritiesService


        if not args:
            print("You'll need to specify coordinates and radius like: London/51.5286416|-0.1015987/100")
            return

        for arg in args:

            # Start the process
            city, coords, radius = arg.split('/')
            print("Fetching information for: {} at {}".format(city, coords, radius))
            city_celebrities = CityCelebritiesService()
            city_celebrities.setup(query=unicode(city))

            location_count = 0
            person_count = 0
            image_count = 0
            hqtext_count = 0
            poortext_count = 0

            for location in city_celebrities.content:
                location_count += 1
                person_count += len(location['people'])
                for person in location['people']:
                    if person['image']:
                        image_count += 1
                    if person['text_quality'] == 1:
                        hqtext_count += 1
                    elif person['text_quality'] < 0:
                        poortext_count += 1
                print location['title'], ' > ', len(location['people'])
                print
                print [person['title'] for person in location['people']]
                print
                print

            print "Location count: {}".format(location_count)
            print "People count: {}".format(person_count)
            print "Images count: {}".format(image_count)
            print "{} high quality, {} low quality and {}, poor quality texts".format(
                hqtext_count,
                person_count - hqtext_count - poortext_count,
                poortext_count
            )
