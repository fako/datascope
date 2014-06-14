from HIF.processes.core import Process, Retrieve, GroupProcess
from HIF.tasks import execute_process, flatten_process_results
from HIF.helpers.mixins import DataMixin


class LocateHistoricalDeaths(Process): #, DataMixin): ?????

    # HIF interface
    HIF_geolocate_model = "WikiGeoSearch"  # HIF.input.http.wiki
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
        source = self.subs["Retrieve"][0]
        source.setup()
        self.rsl = source.results

    class Meta:
        app_label = "HIF"
        proxy = True