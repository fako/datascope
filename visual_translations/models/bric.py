from __future__ import unicode_literals, absolute_import, print_function, division

from collections import OrderedDict
from itertools import groupby
from copy import copy

from core.models.organisms import Community, Collective, Individual


class VisualTranslationsBRICCommunity(Community):

    COMMUNITY_NAME = "visual_translations_bric"

    COMMUNITY_SPIRIT = OrderedDict([
        ("translations", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.query", "$.translate_to"],
                "_kwargs": {},
                "_resource": "WikipediaTranslate",
                "_objective": {
                    "@": "$.page.iwlinks",
                    "language": "$.prefix",
                    "url": "$.url",
                    "word": "$.*",
                },
            },
            "schema": {},
            "errors": {},
        }),
        ("images", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@translations",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.word", "$.country"],
                "_kwargs": {},
                "_resource": "GoogleImage",
                "_objective": {
                    "@": "$.items",
                    "#word": "$.queries.request.0.searchTerms",
                    "#country": "$.queries.request.0.cr",
                    "url": "$.link",
                    "width": "$.image.width",
                    "height": "$.image.height",
                    "thumbnail": "$.image.thumbnailLink",
                },
            },
            "schema": {},
            "errors": {},
        })
    ])

    COMMUNITY_BODY = [
        {
            "process": "ExpansionProcessor.collective_content",
            "config": {}
        }
    ]

    LOCALES = [("pt", "BR",), ("ru", "RU",), ("zh", "CN",), ("zh", "TW",)]

    def initial_input(self, *args):
        collective = Collective.objects.create(
            community=self,
            schema={}
        )
        for language, country in self.LOCALES:
            Individual.objects.create(
                community=self,
                collective=collective,
                properties={
                    "query": args[0],
                    "translate_to": language,
                    "country": "country" + country
                },
                schema={}
            )
        return collective

    def finish_translations(self, out, err):

        new = []
        grouped_translations = out.group_by("language")

        for group, values in groupby(self.LOCALES, lambda el: el[0]):
            locales = list(values)
            for index, value in enumerate(locales):
                language, country = value
                if index == 0:  # only an update needed
                    for ind in grouped_translations[language]:
                        ind.properties["country"] = "country" + country
                else:  # new individuals need to be created
                    def copy_to_country(individual, new_country):
                        new_individual = copy(individual.properties)
                        new_individual["country"] = "country" + new_country
                        return new_individual
                    new += [
                        copy_to_country(ind, country)
                        for ind in grouped_translations[language]
                    ]

        updated = []
        for individuals in grouped_translations.values():
            updated += individuals
        out.update(updated + new)

    def finish_images(self, out, err):
        translations = self.growth_set.filter(type="translations").last()
        grouped_images = out.group_by("word")
        for ind in translations.output.individual_set.all():
            images = [
                image.properties for image in grouped_images[ind.properties["word"]]
                if image.properties["country"] == ind.properties["country"]
            ]
            col = Collective.objects.create(
                community=self,
                schema=out.schema
            )
            col.update(images)
            ind.properties["images"] = col.url
            ind.save()

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="translations").last().output

    class Meta:
        verbose_name = "Visual translation (BRIC)"
        verbose_name_plural = "Visual translations (BRIC)"
