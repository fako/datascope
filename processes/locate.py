from HIF.processes.core import Process, Retrieve, GroupProcess
from HIF.tasks import execute_process, flatten_process_results
from HIF.helpers.mixins import DataMixin
from HIF.exceptions import HIFInputError

class LocateHistoricalDeaths(Process): #, DataMixin): ?????

    # HIF interface
    HIF_geolocate_model = "WikiLocationSearch"  # HIF.input.http.wiki
    HIF_backlinks_model = "WikiBacklinks"  # HIF.input.http.wiki

    HIF_child_process = 'Retrieve'

    def process(self):
        # Get params
        query = self.config.query

        # Setup translate retriever
        geolocate_config = {
            "_link": self.HIF_geolocate_model,
        }
        geolocate_retriever = Retrieve()
        geolocate_retriever.setup(**geolocate_config)

        # Setup image retriever
        backlinks_config = {
            "_link": self.HIF_backlinks_model,
        }
        backlinks_retriever = Retrieve()
        backlinks_retriever.setup(**backlinks_config)

        # Start Celery task
        task = (
            execute_process.s(query, geolocate_retriever.retain()) |
            flatten_process_results.s(key="title") |
            execute_process.s(backlinks_retriever.retain())
        )()
        self.task = task

    def post_process(self):
        from HIF.input.http.wiki import WikiLondenDeath
        source = self.subs["Retrieve"][0]
        source.setup()

        londen_deaths = []
        for rsl in source.results:
            print u"Checking location: {}".format(rsl["query"])
            for page in rsl["results"]:
                print u"Checking page: {}".format(page)
                wld = WikiLondenDeath()
                try:
                    wld.get(page["title"])
                except HIFInputError:
                    print u"Input error, skipped: {}".format(page["title"])
                    continue
                if wld.data:
                    print u"A death: {}".format(page["title"])
                    page["place_of_death"] = wld.data
                    londen_deaths.append(rsl)
                else:
                    print u"Not a death: {}".format(page["title"])
                    continue

        self.rsl = londen_deaths

    class Meta:
        app_label = "HIF"
        proxy = True