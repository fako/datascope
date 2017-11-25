from collections import OrderedDict

from core.models.organisms import Community, Individual


class CommunityMock(Community):

    PUBLIC_CONFIG = {
        "setting1": "const",
        "$setting2": "variable"
    }

    COMMUNITY_SPIRIT = OrderedDict([
        ("phase1", {
            "process": "HttpResourceProcessor.fetch",
            "config": {
                "_args": ["$.test"],
                "_kwargs": {},
                "_resource": "HttpResourceMock",
                "_objective": {
                    "@": "$.dict.list",
                    "value": "$",
                    "#context": "$.dict.test"
                },
            },
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "errors": {
                502: "unreachable",
                404: "not_found"
            },
            "schema": {
                "additionalProperties": False,
                "required": ["context", "value"],
                "type": "object",
                "properties": {
                    "context": {"type": "string"},
                    "value": {"type": "string"}
                }
            },
            "output": "Collective#value",
        }),
        ("phase2", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_args": ["$.value"],
                "_kwargs": {},
                "_resource": "HttpResourceMock",
                "_objective": {
                    "@": "$.dict.list",
                    "value": "$",
                    "#context": "$.dict.test"
                },
            },
            "input": "@phase1",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "errors": {},
            "schema": {
                "additionalProperties": False,
                "required": ["context", "value"],
                "type": "object",
                "properties": {
                    "context": {"type": "string"},
                    "value": {"type": "string"}
                }
            },
            "output": "&input"
        }),
        ("phase3", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_args": ["$.value"],
                "_kwargs": {},
                "_resource": "HttpResourceMock",
            },
            "input": "@phase2",
            "contribute": None,
            "errors": {},
            "output": "Individual",
            "schema": {}
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "MockNumberProcessor.number_individuals",
            "config": {}
        },
        {
            "name": "filter_individuals",
            "process": "MockFilterProcessor.filter_individuals",
            "config": {}
        },
    ]

    def initial_input(self, *args):
        return Individual.objects.create(
            properties={"test": "test"},
            schema={},
            community=self
        )

    def begin_phase1(self, inp):
        return

    def finish_phase2(self, out, err):
        return

    def error_phase1_unreachable(self, err, out):
        return True  # continue if there are results

    def error_phase1_not_found(self, err, out):
        return False  # abort community

    def before_filter_individuals_manifestation(self, part):
        return

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="phase3").last().output
        super(CommunityMock, self).set_kernel()
