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
            city_celebrities = CityCelebrities()
            city_celebrities.execute(coords=coords)

            # Finish the process synchronously
            city_celebrities.task.get()
            city_celebrities.execute(coords=coords)

            if city_celebrities.status != ProcessStatus.DONE:
                print("City Celebrities process failed with: {}".format(city_celebrities.status))
                return

            print("Fetching claims information for all backlinks of locations")

            locations = []
            for location in city_celebrities.rsl[:10]:

                if "backlinks" not in location:
                    print("Skipping location due to lack of backlinks: " + location['title'])
                    continue

                print("Next up location: " + location['title'])
                human = {
                    "property": "P31",
                    "item": 5
                }
                people = []
                for page in location['backlinks']:
                    retriever = Retrieve()
                    retriever.execute(page['wikidata'], _link="WikiDataClaims", excluded_properties=[])

                    if retriever.status != ProcessStatus.DONE:
                        print("Skipping due to failed retriever: " + location['title'])
                        continue

                    claims = retriever.rsl

                    if human not in claims:
                        print("Backlink is not human: " + page['title'])
                        continue

                    print("Adding backlink to people set: " + page['title'])
                    page['claims'] = claims
                    people.append(page)

                if not people:
                    print("Skipping location due to lack of people backlinks: " + location['title'])
                    continue

                location['people'] = people
                del(location['backlinks'])
                locations.append(location)

            cc_service = CityCelebritiesService()
            cc_service.setup({"query": city})
            cc_service.content = locations
            cc_service.retain()
