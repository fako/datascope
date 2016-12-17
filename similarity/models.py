from collections import OrderedDict

from core.models.organisms import Community, Individual


class WikipediaCategorySimularityCommunity(Community):
    COMMUNITY_NAME = "visual_translations_bric"

    COMMUNITY_SPIRIT = OrderedDict([
        ("search", {
            "process": "HttpResourceProcessor.fetch",
            "input": None,
            "contribute": "Update:ExtractProcessor.extract_from_resource",
            "output": "&input",
            "config": {
                "_args": ["$.title"],
                "_kwargs": {},
                "_resource": "WikipediaSearch",
                "_objective": {
                    "@": "$.query.pages",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "wikidata": "$.pageprops.wikibase_item",
                    "image": "$.pageprops.page_image_free",
                },
                "_update_key": "title"
            },
            "schema": {},
            "errors": {
                300: "ambiguous",
                404: "not_found"
            },
        }),
        # ("categories", {
        #     "process": "HttpResourceProcessor.fetch_mass",
        #     "input": "@translations",
        #     "contribute": "Append:ExtractProcessor.extract_from_resource",
        #     "output": "Collective",
        #     "config": {
        #         "_args": ["$.word", "$.country"],
        #         "_kwargs": {},
        #         "_resource": "GoogleImage",
        #         "_objective": {
        #             "@": "$.items",
        #             "#word": "$.queries.request.0.searchTerms",
        #             "#country": "$.queries.request.0.cr",
        #             "url": "$.link",
        #             "width": "$.image.width",
        #             "height": "$.image.height",
        #             "thumbnail": "$.image.thumbnailLink",
        #         },
        #         "_continuation_limit": 10
        #     },
        #     "schema": {},
        #     "errors": {},
        # }),
        # ("members", {
        #     "process": "HttpResourceProcessor.fetch_mass",
        #     "input": "@translations",
        #     "contribute": "Append:ExtractProcessor.extract_from_resource",
        #     "output": "Collective",
        #     "config": {
        #         "_args": ["$.word", "$.country"],
        #         "_kwargs": {},
        #         "_resource": "GoogleImage",
        #         "_objective": {
        #             "@": "$.items",
        #             "#word": "$.queries.request.0.searchTerms",
        #             "#country": "$.queries.request.0.cr",
        #             "url": "$.link",
        #             "width": "$.image.width",
        #             "height": "$.image.height",
        #             "thumbnail": "$.image.thumbnailLink",
        #         },
        #         "_continuation_limit": 10
        #     },
        #     "schema": {},
        #     "errors": {},
        # })
    ])

    COMMUNITY_BODY = [
        # {
        #     "process": "ExpansionProcessor.collective_content",
        #     "config": {}
        # }
    ]

    def initial_input(self, *args):
        return Individual.objects.create(community=self, schema={}, properties={
            "title": args[0]
        })

    def error_search_ambiguous(self, errors, out):
        return False

    def error_search_not_found(self, errors, out):
        return False

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="search").last().input
