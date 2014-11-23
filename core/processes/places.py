import requests

from core.processes.base import Process, Retrieve
from core.tasks import execute_process, extend_process


class CityCelebrities(Process):

    HIF_geo_lookup = 'WikiGeo'
    HIF_backlinks = 'WikiBacklinks'

    def process(self):

        # Get process input
        coords = self.config.coords
        radius = self.config.radius

        # Setup person retriever
        geo_lookup_config = {
            "_link": self.HIF_geo_lookup,
            "radius": radius
        }
        geo_lookup_config.update(self.config.dict())
        geo_lookup_retriever = Retrieve()
        geo_lookup_retriever.setup(**geo_lookup_config)

        # Setup data retriever
        backlinks_config = {
            "_link": self.HIF_backlinks,
            "_context": "{}+{}".format(coords, radius),  # here only to distinct inter-query retriever configs from each other
            "_extend": {
                "source": None,
                "target": "*",
                "args": "*.title",
                "kwargs": {},
                "extension": "backlinks"
            }
        }
        backlinks_retriever = Retrieve()
        backlinks_retriever.setup(**backlinks_config)

        # Start Celery task
        task = (
            execute_process.s(coords, geo_lookup_retriever.retain()) |
            extend_process.s(backlinks_retriever.retain())
        )()
        self.task = task

    def post_process(self):

        results = Retrieve().load(serialization=self.task.result).rsl

        all_items = []
        for location in results:
            for link in location['backlinks']:
                all_items.append(link['wikidata'])

        # TODO: create a process to do the filtering
        filtered_items = []
        while(all_items):
            batch = all_items[:500]
            all_items = all_items[500:] if len(all_items) > 500 else []
            query = "ITEMS[{}] AND CLAIM[31:5] AND NOCLAIM[570]".format(", ".join([item[1:] for item in batch]))
            response = requests.post('http://wdq.wmflabs.org/api', {"q": query})
            filtered_items += response.json()['items']

        filtered_locations = []
        for location in results:
            filtered_links = []
            for link in location['backlinks']:
                if link['wikidata'] and int(link['wikidata'][1:]) in filtered_items:  # strips 'Q' from items and makes it int
                    filtered_links.append(link)
            if len(filtered_links):
                location['people'] = filtered_links
                del location['backlinks']
                filtered_locations.append(location)

        self.rsl = filtered_locations

    class Meta:
        app_label = "core"
        proxy = True