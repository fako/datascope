from HIF.processes.core import Process, Retrieve
from HIF.tasks import execute_process, extend_process
from HIF.helpers.storage import get_hif_model
from HIF.helpers.data import count_2d_list



class PeopleSuggestions(Process):

    HIF_person_lookup = 'WikiSearch'
    HIF_person_claims = 'WikiDataClaims'
    HIF_claimers = 'WikiDataClaimers'

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

        # Setup claimers finder
        claimers_config = {
            "_link": self.HIF_claimers,
            "_extend": {
                "keypath": "claims",
                "args": [None],  # entire dict at keypath will become args
                "kwargs": {},
                "extension": "claimers"
            }
        }
        claimers_retriever = Retrieve()
        claimers_retriever.setup(**claimers_config)

        # Start Celery task
        task = (
            execute_process.s(query, person_lookup_retriever.retain()) |
            extend_process.s(person_claims_retriever.retain()) |
            extend_process.s(claimers_retriever.retain(), multi=True)
        )()
        self.task = task

    def post_process(self):
        person_data = Retrieve().load(serialization=self.task.result).rsl
        self.rsl = count_2d_list(person_data['claims'], d2_list='claimers').most_common(11)[1:]  # takes 10, but strips query person

    class Meta:
        app_label = "HIF"
        proxy = True