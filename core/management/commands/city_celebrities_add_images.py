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
        from core.input.http.wiki import WikiBaseQuery
        from core.processes.base import Retrieve
        from core.output.http.services.manifests import CityCelebritiesService
        import hashlib


        if not args:
            print("You'll need to specify coordinates like: London/51.5286416|-0.1015987")
            return

        for arg in args:

            # Start the process
            city, coords = arg.split('/')
            print("Fetching information for: {} at {}".format(city, coords))
            city_celebrities = CityCelebritiesService()
            city_celebrities.setup(query=unicode(city))

            wbq = WikiBaseQuery()
            wbq.get("|".join([page['title'] for page in city_celebrities.content]))

            new_locations = []
            for location in city_celebrities.content:

                for page in wbq.data:

                    if page['title'] == location['title'] and page['image']:
                        md5 = hashlib.md5()
                        md5.update(page['image'])
                        hexhash = md5.hexdigest()
                        location['image'] = 'http://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'.format(
                            hexhash[:1],
                            hexhash[:2],
                            page['image']
                        )

                if 'image' in location:
                    new_locations.append(location)

            city_celebrities.content = new_locations
            city_celebrities.save()
