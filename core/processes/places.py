import re
import requests

from core.processes.base import Process, Retrieve
from core.tasks import execute_process, extend_process


class FilterPeople(Process):

    def process(self):

        results = Process().load(serialization=self.config._continue).rsl

        all_items = []
        for location in results:
            for link in location['backlinks']:
                all_items.append(link['wikidata'])

        # TODO: create link type that does POST and is convenient for logic below
        filtered_items = []
        while all_items:
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


class CityCelebrities(Process):

    HIF_geo_lookup = 'WikiGeo'
    HIF_backlinks = 'WikiBacklinks'
    HIF_info = 'WikiSearch'

    def process(self):

        # Get process input
        coords = self.config.coords
        radius = self.config.radius

        # Setup person retriever
        geo_lookup_config = {
            "_link": self.HIF_geo_lookup,
            "radius": radius,
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

        filter_config = {
            "_continue": geo_lookup_retriever.retain(),
            "_context": "{}+{}".format(coords, radius)
        }
        filter_process = FilterPeople()
        filter_process.setup(**filter_config)

        text_config = {
            "_link": self.HIF_info,
            "_context": "{}+{}".format(coords, radius),  # here only to distinct inter-query retriever configs from each other
            "extracts": True,
            "_extend": {
                "source": None,
                "target": "*.people.*",
                "args": "*.people.*.title",
                "kwargs": {},
                "extension": None
            }
        }
        text_process = Retrieve()
        text_process.setup(**text_config)

        location_config = {
            "_link": self.HIF_info,
            "_context": "{}+{}".format(coords, radius),  # here only to distinct inter-query retriever configs from each other
            "extracts": True,
            "_extend": {
                "source": None,
                "target": "*",
                "args": "*.title",
                "kwargs": {},
                "extension": None
            }
        }
        location_process = Retrieve()
        location_process.setup(**location_config)

        # Start Celery task
        task = (
            execute_process.s(coords, geo_lookup_retriever.retain()) |
            extend_process.s(backlinks_retriever.retain()) |
            execute_process.s(filter_process.retain()) |
            extend_process.s(text_process.retain()) |
            extend_process.s(location_process.retain())
        )()
        self.task = task

    def post_process(self):
        results = Retrieve().load(serialization=self.task.result).rsl

        locations = []
        for location in results:
            people = []
            for person in location['people']:
                person['text'], person['text_quality'] = self.select_paragraph(location, person)
                del person['extract']  # way too big for a response
                people.append(person)
            location['people'] = people
            locations.append(location)

        self.rsl = locations

    @staticmethod
    def select_paragraph(location, person):
        match = re.search(r'<p>.*?{}.*?</p>'.format(location['title']), person['extract'], re.DOTALL)
        text_quality = 1
        if match is None:
            match = re.search(r'<p>.*?</p>', person['extract'], re.DOTALL)
            text_quality = 0
        return match.group(0), text_quality

    class Meta:
        app_label = "core"
        proxy = True