from __future__ import unicode_literals, absolute_import, print_function, division
import six

from collections import OrderedDict
from itertools import groupby
from copy import copy

from django.core.files.storage import default_storage

from core.models.organisms import Community, Collective, Individual
from core.utils.image import ImageGrid
from core.processors.expansion import ExpansionProcessor

from sources.models.downloads import ImageDownload


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
        }),
        ("download", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@images",
            "contribute": None,
            "output": None,
            "config": {
                "_args": ["$.url"],
                "_kwargs": {},
                "_resource": "ImageDownload"
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
        ("de", "AT", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("nl", "BE", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("fr", "BE", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("bg", "BG", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("hr", "HR", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("el", "CY", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("cs", "CZ", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("da", "DK", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("et", "EE", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("fi", "FI", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("fr", "FR", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("de", "DE", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("el", "GR", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("hu", "HU", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("it", "IT", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("lt", "LT", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("lv", "LV", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("fr", "LU", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("mt", "MT", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("nl", "NL", {"columns": 2, "rows": 4, "cell_width": 320, "cell_height": 180},),
        ("pl", "PL", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("pt", "PT", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("ro", "RO", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("sk", "SK", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("sl", "SI", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("es", "ES", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("sv", "SE", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("en", "GB", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
        ("en", "IR", {"columns": 4, "rows": 3, "cell_width": 320, "cell_height": 180},),
    ]

    # TODO: don't hard code the source language

    def initial_input(self, *args):
        collective = Collective.objects.create(
            community=self,
            schema={}
        )
        query = args[0]
        # TODO: create dir here
        for language, country, grid in self.LOCALES:
            if language == "en":
                continue
            Individual.objects.create(
                community=self,
                collective=collective,
                properties={
                    "query": query,
                    "translate_from": "en",
                    "translate_to": language,
                    "country": "country" + country
                },
                schema={}
            )
        return collective

    def finish_translations(self, out, err):
        new = []
        group_lambda = lambda el: el[0]
        for group, values in groupby(sorted(self.LOCALES, key=group_lambda), group_lambda):
            locales = list(values)

            individuals = out.individual_set.all()
            for index, value in enumerate(locales):
                language, country, grid = value

                if language == "en":  # creating individuals for untranslated words
                    translations = self.growth_set.filter(type="translations").last()
                    inp = translations.input.individual_set.first()
                    new.append({
                        "country": "country" + country,
                        "language": "en",
                        "word": inp.properties["query"],
                        "confidence": None,
                        "meanings": None,
                        "locale": "{}_{}".format(language, country)
                    })
                elif index == 0:  # only an update needed
                    for ind in individuals:  # TODO: simplify by using Collective.select (re-use querysets!)
                        if ind.properties["language"] != language:
                            continue
                        ind.properties["country"] = "country" + country
                        ind.properties["locale"] = "{}_{}".format(language, country)
                        new.append(ind)
                else:  # new individuals need to be created
                    for ind in individuals:  # TODO: simplify by using Collective.select (re-use querysets!)
                        if ind.properties["language"] != language:
                            continue
                        properties = copy(ind.properties)
                        properties["country"] = "country" + country
                        properties["locale"] = "{}_{}".format(language, country)
                        new.append(properties)
        if new:
            out.update(new)

    def finish_images(self, out, err):
        translations = self.growth_set.filter(type="translations").last()
        grouped_images = out.group_by("word")
        for ind in translations.output.individual_set.all():
            images = [
                image for image in grouped_images.get(ind.properties["word"], [])
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

    zoom_levels = {"S": 0.2, "L": 1}

    def finish_download(self, out, err):  # TODO: move images in downloads folder? another way?
        translation_growth = self.growth_set.filter(type="translations").last()
        grids = {"{}_{}".format(language, country): grid for language, country, grid in self.LOCALES}
        grouped_translations = translation_growth.output.group_by("locale")
        for locale, translations in six.iteritems(grouped_translations):
            expansion_processor = ExpansionProcessor()
            translations = expansion_processor.collective_content(
                [translation.properties for translation in translations]
            )
            images = []
            query = translation_growth.input.individual_set.last().properties["query"]
            for translation in translations:
                for image in translation["images"]:
                    images.append(image)
            downloads_queryset = ImageDownload.objects.filter(
                uri__in=[ImageDownload.uri_from_url(image["url"]) for image in images]
            )
            downloads = []
            for download in downloads_queryset:
                content_type, image = download.content
                if image is not None:
                    downloads.append(image)
            for size, factor in self.zoom_levels.iteritems():
                grid_specs = copy(grids[locale])
                grid_specs["cell_width"] = int(grid_specs["cell_width"] * factor)
                grid_specs["cell_height"] = int(grid_specs["cell_height"] * factor)
                image_grid = ImageGrid(**grid_specs)
                image_grid.fill(downloads)
                image_grid.export("visual_translations/{}/{}_{}.jpg".format(query, size, locale))

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="translations").last().output

    class Meta:
        verbose_name = "Visual translation"
        verbose_name_plural = "Visual translations"
