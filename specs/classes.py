# THINK: make it possible to store some of the context of responses inside Individuals.

from collections import OrderedDict

from core.models.organisms.community import Community


class ImageTranslations(Community):

    spirit = OrderedDict([
        ("translation", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiTranslate"
            },
            "errors": {
                404: "translation_404"
            },
            "input": (
                "Collective",
                ("$.source", "$.target", "$.query"),
                tuple()
            ),  # leaves it to capture_initial_incoming to provide this
            "schema": {},
            "transformations": {},
            "output": "Collective",
        }),
        ("images", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "GoogleImages"
            },
            "errors": {},
            "input": (
                "$.translation.outgoing",
                ("$.word",),
                tuple()
            ),
            "schema": {},
            "transformations": {},
            "outgoing": "Collective",
            "actions": ["fetch_more_images"]
        })
    ])

    def setup_translation(self, input_organism):
        """
        Should return a tuple in format of (tuple, dict) which will be passed directly into the specified process.

        :param incoming:
        :return:
        """


    def fetch_more_images(self, post_data):
        """
        Takes a list of Individual ids inside of post_data that were gathered by the translation growth.
        It will get a processor from the visualization growth and add images to the Collectives referenced by the individuals.
        These images should come from the processor response when using Individual.more_visuals_url as URL.

        :param post_data:
        :return:
        """

    @property
    def kernel(self):
        """

        :return: spirit that is the base for results
        """
        return "translation"

    def setup_visualization(self, incoming):
        """
        Should return a tuple in format of (tuple, dict) which will be passed directly into the specified process.

        :param incoming:
        :return:
        """

    def after_visualization(self, input_organism, output_organism):
        """
        Add visualizations and the more_visualization to all translations

        :param growth:
        :param output:
        :return:
        """
        pass

    def translation_404(self, resources):
        pass


class PeopleSuggestions(Community):
    spirit = OrderedDict([
        ("person", {
            "schema": {},
            "config": {
                "_link": "WikiSearch"
            },
            "process": "Retrieve",
            "input": None,
            "output": "Individual",

        }),
        ("categories", {
            "schema": {},
            "config": {
                "_link": "WikiCategories"
            },
            "process": "Retrieve",
            "input": "/ind/1/#$.title",
            "output": "Collective"
        }),
        ("members", {
            "schema": {},
            "config": {
                "_link": "WikiCategoryMembers"
            },
            "process": "Retrieve",
            "input": "/col/1/#$.title",
            "output": "Collective"
        })
    ])


class CityCelebrities(Community):
    spirit = OrderedDict([
        ("radius", {
            "process": "HttpResourceProcessor.fetch",
            "config": {
                "_resource": ""
            },
            "errors": {},
            "input": ("Individual", ("$.latitude", "$.longitude",), tuple()),  # should be coords
            "schema": {},
            "transformations": {},
            "output": "Collective"
        }),
        ("backlinks", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resouce": "WikiBacklinks",
            },
            "errors": {},
            "input": ("$.radius.output", ("title",), tuple()),
            "schema": {},
            "transformations": {},
            "output": "Collective"
        }),
        ("people_filter", {
            "process": "HttpResourceProcessor.submit_mass",
            "config": {
                "_resource": "WikiDataFilter",
                "concat_args_with": ",",
                "wdq_template": "ITEMS[{}] AND CLAIM[31:5] AND NOCLAIM[570]"
            },
            "errors": {},
            "input": ("$.backlinks.output", ("wikidata",), tuple()),
            "schema": {},
            "transformations": {},
            "output": "Individual"
        }),
        ("people_text", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiSearch",
                "concat_with": ","
            },
            "errors": {},
            "input": ("$.backlinks.output", ("id",), tuple()),
            "schema": {},
            "transformations": {},
            "output": "Collective"
        }),
        ("location_text", {
            "process": "HttpResourceProcessor.fetch_mass",
            "config": {
                "_resource": "WikiSearch",
                "concat_with": ","
            },
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


class FamousFlightDeaths(Community):
    pass
