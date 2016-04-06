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
    #
    # PUBLIC_CONFIG = {
    #     "$revision_count": 1,
    #     "$category_count": 1,
    # }
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

    def finish_translations(self, out, err):  # TODO: optimize using "meta" properties
        new = []
        for group, values in groupby(self.LOCALES, lambda el: el[0]):
            locales = list(values)
            individuals = out.individual_set.all()
            for index, value in enumerate(locales):
                language, country = value
                if index == 0:  # only an update needed
                    for ind in individuals:
                        if ind.properties["language"] != language:
                            continue
                        ind.properties["country"] = "country" + country
                        ind.save()
                else:  # new individuals need to be created
                    for ind in individuals:
                        if ind.properties["language"] != language:
                            continue
                        properties = copy(ind.properties)
                        properties["country"] = "country" + country
                        new.append(properties)
            if new:
                out.update(new)

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
