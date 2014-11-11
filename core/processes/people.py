from core.processes.base import Process, Retrieve
from core.tasks import execute_process, extend_process
from core.helpers.data import count_2d_list


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
            "_context": query,  # here only to distinct inter-query retriever configs from each other
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
            "_context": query,  # here only to distinct inter-query retriever configs from each other
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
        people_raw = count_2d_list(person_data['claims'], d2_list='claimers').most_common(11)[1:]  # takes 10, but strips query person

        people = []
        for person_raw in people_raw:

            person = {
                "item": person_raw[0],
                "matches": person_raw[1],
                "properties": [],
                "items": []
            }

            for claim in person_data['claims']:
                if person['item'] in claim['claimers']:
                    person['properties'].append(claim['property'])
                    person['items'].append(claim['item'])

            people.append(person)

        self.rsl = people

    class Meta:
        app_label = "core"
        proxy = True