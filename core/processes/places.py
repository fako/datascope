from core.processes.base import Process, Retrieve
from core.tasks import execute_process, extend_process

# TODO: update for new style extend
class CityCelebrities(Process):

    HIF_geo_lookup = 'WikiGeo'
    HIF_backlinks = 'WikiBacklinks'

    def process(self):

        # Get process input
        coords = self.config.coords

        # Setup person retriever
        geo_lookup_config = {
            "_link": self.HIF_geo_lookup,
        }
        geo_lookup_config.update(self.config.dict())
        geo_lookup_retriever = Retrieve()
        geo_lookup_retriever.setup(**geo_lookup_config)

        # Setup data retriever
        backlinks_config = {
            "_link": self.HIF_backlinks,
            "_context": coords,  # here only to distinct inter-query retriever configs from each other
            "_extend": {
                "keypath": None,
                "args": ["title"],
                "kwargs": {},
                "extension": "backlinks"
            }
        }
        backlinks_retriever = Retrieve()
        backlinks_retriever.setup(**backlinks_config)

        # Start Celery task
        task = (
            execute_process.s(coords, geo_lookup_retriever.retain()) |
            extend_process.s(backlinks_retriever.retain(), multi=True)
        )()
        self.task = task

    def post_process(self):
        self.rsl = Retrieve().load(serialization=self.task.result).rsl

    class Meta:
        app_label = "core"
        proxy = True