from celery import group

from HIF.processes.core import Process, Retrieve, GroupProcess
from HIF.tasks import execute_process, flatten_process_results, extend_process
from HIF.helpers.mixins import DataMixin


class PeopleSuggestion(Process):

    HIF_person_lookup = 'WikiSearch'
    HIF_person_claims = 'WikiDataClaims'

    def process(self):

        # Get process input
        query = self.config.query

        # Setup person retriever
        person_lookup_config = {
            "_link": self.HIF_person_lookup,
        }
        person_lookup_config.update(self.config.dict())
        person_lookup_retriever = Retrieve()
        person_lookup_retriever.setup(**person_lookup_config)

        # Setup data retriever
        person_claims_config = {
            "_link": self.HIF_person_claims,
            "_extend": {
                "keypath": None,
                "args": ["wikidata"],
                "kwargs": {},
                "extension": "claims"
            }
        }
        person_claims_retriever = Retrieve()
        person_claims_retriever.setup(**person_claims_config)

        # Register processes
        # TODO: Substorage should be ManyToMany based, in order to handle registration automatically
        person_lookup_retriever.subs.add(person_claims_retriever.retain())

        # Start Celery task
        task = (
            execute_process.s(query, person_lookup_retriever.retain()) |
            extend_process.s(person_claims_retriever.retain())
        )()
        self.task = task

    def post_process(self):
        # self.task.result (serialization)
        pass

    class Meta:
        app_label = "HIF"
        proxy = True