from collections import OrderedDict

from django.db import models

from jsonfield import JSONField

from core.models.organisms.community import Community


class ImageTranslations(Community):
    spirit = OrderedDict([
        ("translation", {
            "process": "Retrieve",
            "config": {
                "_resource": "WikiTranslate"
            },
            "errors": {
                300: "translation_300",
                404: "translation_404"
            },
            "input": "Individual",
            "context": {},
            "schema": {},
            "transformations": {},
            "output": "Collective",
            "actions": ["fetch_more_images"]
        }),
        ("visualization", {
            "schema": {},
            "config": {
                "_resource": "GoogleImages|YouTubeSearch"
            },
            "process": "Retrieve",
            "input": "Collective",
            "context": {},
            "output": "Collective"
        })
    ])

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

    def before_translation(self, growth):
        """
        Use self.path to set initial input

        :param growth:
        :return:
        """
        pass

    def after_visualization(self, growth, output):
        """
        Add visualizations and the more_visualization to all translations

        :param growth:
        :param output:
        :return:
        """
        pass

    def translation_300(self, resources):
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
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": None,
            "output": "Collective"
        }),
        ("backlinks", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/col/1/#$.title",
            "output": "Collective"
        }),
        ("people_filter", {
            "schema": {},
            "config": {},
            "process": "Submit",
            "input": "/col/2/#$.wikidata",
            "output": "Collective"
        }),
        ("people_text", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/col/3/#$.title",
            "output": "Collective"
        }),
        ("location_text", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/col/1/",
            "output": "Collective"
        })
    ])


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
