from collections import OrderedDict

from core.models.organisms.community import Community


class ImageTranslations(Community):

    PUBLIC_CONFIG = {
        "source_language": "en",
        "$depth": 0
    }

    COMMUNITY_SPIRIT = OrderedDict([
        ("translation", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiTranslate",
                "_objective": {},
                "source_language": "en"
            },
            "input": (
                "Collective",  # leaves it to capture_initial_input to provide this
                ("$.language", "$.target", "$.query"),
                tuple()
            ),
            "success": "ExtractProcessor.extract_resource",
            "errors": {
                404: "not_found"
            },
            "schema": {},
            "output": "Collective",
        }),
        ("images", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "GoogleImages",
                "_objective": {}
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": (
                "@translation",
                ("$.word",),
                tuple()
            ),
            "schema": {},
            "output": "Collective",
            "actions": ["fetch_more_images"]
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "Expand.nested_organisms",
            "config": {
                "depth": 0,
                "keys": ["images"]
            }
        }
    ]

    def error_translation_not_found(self, errors, output):
        pass

    def set_kernel(self):
        """
        Add visualizations and the more_visualization to all translations

        :param growth:
        :param output:
        :return:
        """
        pass

    def fetch_more_images(self, post_data):
        """
        Takes a list of Individual ids inside of post_data that were gathered by the translation growth.
        It will get a processor from the visualization growth and add images to the Collectives referenced by the individuals.
        These images should come from the processor response when using Individual.more_visuals_url as URL.

        :param post_data:
        :return:
        """
        pass


class PeopleSuggestions(Community):

    PUBLIC_CONFIG = {}

    spirit = OrderedDict([
        ("person", {
            "process": "HttpResourceProcessor.fetch",
            "config": {
                "_resource": "WikiSearch",
                "_objective": {},
                "props": "categories"
            },
            "input": (
                "Individual",  # leaves it to capture_initial_input to provide this
                ("$.person",),
                tuple()
            ),
            "success": "ExtractProcessor.extract_resource",
            "errors": {
                300: "multiple_choice",
                404: "not_found"
            },
            "schema": {},
            "output": "Individual",
        }),
        ("members", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiCategoryMembers",
                "_objective": {}
            },
            "success": "ExtractProcessor.extract_resource",
            "errors": {},
            "input": (
                "$.translation.output",
                ("$.categories[*].title",),
                tuple()
            ),
            "schema": {},
            "output": "Collective",
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "Rank.weights_in",
            "config": {
                "path": "$.categories",
            }
        }
    ]

    def error_person_not_found(self):
        pass

    def error_person_multiple_choice(self):
        pass

    def set_kernel(self):
        pass


class CityCelebrities(Community):
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


class PersonProfile(Community):
    spirit = OrderedDict([
        ("auth", {
            "schema": {},
            "config": {},
            "process": "Authenticate",
            "input": None,
            "output": "Individual"
        }),
        ("profile", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "Individual",
            "output": "Individual"
        }),
        ("basics", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Individual"
        }),
        ("friends", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Collective"
        }),
        ("likes", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Collective"
        }),
        ("photos", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Collective"
        })
    ])


class WikiNewsFeed(Community):
    pass


class FamousFlightDeaths(Community):
    pass


class CommunityPortal(Community):
    pass


class SynonymImages(Community):
    pass


class FindSimilar(Community):
    pass