from __future__ import unicode_literals, absolute_import, print_function, division

from collections import OrderedDict
from itertools import groupby
from copy import copy

from core.models.organisms import Community, Collective, Individual


class VisualTranslationsCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("translations", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["translate_from", "$.translate_to", "$.query"],
                "_kwargs": {},
                "_resource": "GoogleTranslate",
                "_objective": {
                    "@": "$",
                    "language": "$.language",
                    "word": "$.word",
                    "confidence": "$.confidence",
                    "meanings": "$.meanings"
                },
                "_interval_duration": 2500
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

    LOCALES = [
        ("de", "AT",),
        ("nl", "BE",), ("fr", "BE",),
        ("bg", "BG",),
        ("hr", "HR",),
        ("el", "CY",),
        ("cs", "CZ",),
        ("da", "DK",),
        ("et", "EE",),
        ("fi", "FI",),
        ("fr", "FR",),
        ("de", "DE",),
        ("el", "GR",),
        ("hu", "HU",),
        ("it", "IT",),
        ("lt", "LT",),
        ("lv", "LV",),
        ("fr", "LU",),
        ("mt", "MT",),
        ("nl", "NL",),
        ("pl", "PL",),
        ("pt", "PT",),
        ("ro", "RO",),
        ("sk", "SK",),
        ("sl", "SI",),
        ("es", "ES",),
        ("sv", "SE",),
        ("en", "GB",),
        ("en", "IR",),
    ]

    # TODO: don't hard code the source language

    def initial_input(self, *args):
        collective = Collective.objects.create(
            community=self,
            schema={}
        )
        for language, country in self.LOCALES:
            if language == "en":
                continue
            Individual.objects.create(
                community=self,
                collective=collective,
                properties={
                    "query": args[0],
                    "translate_from": "en",
                    "translate_to": language,
                    "country": "country" + country
                },
                schema={}
            )
        return collective

    def finish_translations(self, out, err):  # TODO: optimize using "meta" properties
        new = []
        group_lambda = lambda el: el[0]
        for group, values in groupby(sorted(self.LOCALES, key=group_lambda), group_lambda):
            locales = list(values)

            individuals = out.individual_set.all()
            for index, value in enumerate(locales):
                language, country = value

                if language == "en":  # creating individuals for untranslated words
                    translations = self.growth_set.filter(type="translations").last()
                    inp = translations.input.individual_set.first()  # TODO: optimize
                    new.append({
                        "country": "country" + country,
                        "language": "en",
                        "word": inp.properties["query"],
                        "confidence": None,
                        "meanings": None,
                    })
                elif index == 0:  # only an update needed
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
                image.properties for image in grouped_images.get(ind.properties["word"], [])
                if image.properties["country"] == ind.properties["country"]
            ]
            if not images:
                translations.output.individual_set.remove(ind)
                continue

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
        verbose_name = "Visual translation"
        verbose_name_plural = "Visual translations"
