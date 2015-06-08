from collections import OrderedDict

from core.models.organisms.community import Community


class WikiNewsCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("wikipedia", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_args": [],
                "_kwargs": {},
                "_resource": "WikipediaRecentChanges",
                "_objective": {
                    "@": "$.query.recentchanges",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "timestamp": "$.timestamp",
                    "comment": "$.comment"
                },
                "source_language": "en"
            },
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_resource",
            "errors": {},
            "schema": {},
            "output": "Collective",
        })
    ])
