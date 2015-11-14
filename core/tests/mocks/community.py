from collections import OrderedDict

from core.models.organisms import Community, Individual


class CommunityMock(Community):

    PUBLIC_CONFIG = {
        "setting1": "const",
        "$setting2": "variable"
    }

    COMMUNITY_SPIRIT = OrderedDict([
        ("phase1", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_args": ["$.start"],
                "_kwargs": {},
                "_resource": "HttpResourceMock",
                "_objective": {
                    "@": "$.dict.list",
                    "value": "$",
                    "#context": "$.dict.test"
                },
            },
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_resource",
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
            "output": "Collective",
        }),
        ("phase2", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_args": ["$.start"],
                "_kwargs": {},
                "_resource": "HttpResourceMock",
                "_objective": {
                    "@": "$.dict.list",
                    "value": "$",
                    "#context": "$.dict.test"
                },
            },
            "input": "@phase1",
            "contribute": "Append:ExtractProcessor.extract_resource",
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
            "output": "Collective",  # TODO: make this individual
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "MockNumberProcessor.number_individuals",
            "config": {}
        },
        {
            "process": "MockFilterProcessor.filter_individuals",
            "config": {}
        },
    ]

    def initial_input(self):
        return Individual.objects.create(
            properties={"test": "test"},
            schema={},
            community=self
        )

    def begin_phase1(self, inp):
        return

    def finish_phase2(self, out, err):
        return

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="phase2").last().output
