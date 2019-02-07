# This is a legacy declaration of an interesting service
# It finds backlinks to local Wikipedia articles
# Could act like a tourist guide of some kind
from collections import OrderedDict


class CityCelebrities(object):
    spirit = OrderedDict([
        ("radius", {
            "process": "HttpResourceProcessor.fetch",
            "config": {
                "_resource": "WikiGeoLocation",
                "_objective": {}
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": ("Individual", ("$.latitude", "$.longitude",), tuple()),
            "schema": {},
            "output": "Collective",
        }),
        ("backlinks", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiBacklinks",
                "_objective": {}
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": ("$.radius.output", ("$.title",), tuple()),
            "schema": {},
            "output": "Collective"
        }),
        ("people_filter", {
            "process": "HttpResourceProcessor.submit_mass",
            "config": {
                "_resource": "WikiDataFilter",
                "concat_args_with": ",",
                "wdq_template": "ITEMS[{}] AND CLAIM[31:5] AND NOCLAIM[570]"
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": ("@backlinks", ("$.wikidata",), tuple()),
            "schema": {},
            "output": "Collective"
        }),
        ("people_text", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiSearch",
                "concat_args_with": ",",
                "_objective": {}
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": ("@backlinks", ("id",), tuple()),
            "schema": {},
            "transformations": {},
            "output": "Collective"
        }),
        ("location_text", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiSearch",
                "concat_with": ",",
                "_objective": {}
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": ("$.radius.output", ("id",), tuple()),
            "schema": {},
            "transformations": {},
            "output": "Collective"
        })
    ])

    def setup_backlinks(self, incoming):
        pass

    def finish_people_filter(self):
        """
        Will remove items from backlinks.output based on people_filter.output

        :return:
        """
        pass

    def set_kernel(self):
        pass
