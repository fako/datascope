from __future__ import unicode_literals, absolute_import, print_function, division

from collections import OrderedDict
from itertools import groupby
from copy import copy

from core.models.organisms import Community, Collective, Individual


class VisualTranslationCommunity(Community):

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
        # ("pages", {
        #     "process": "HttpResourceProcessor.fetch_mass",
        #     "input": "@revisions",
        #     "contribute": "Append:ExtractProcessor.extract_from_resource",
        #     "output": "Collective",
        #     "config": {
        #         "_args": ["$.pageid"],
        #         "_kwargs": {},
        #         "_resource": "WikipediaListPages",
        #         "_objective": {
        #             "@": "$.query.pages",
        #             "pageid": "$.pageid",
        #             "title": "$.title",
        #             "categories": "$.categories",
        #             "image": "$.pageprops.page_image",
        #             "wikidata": "$.pageprops.wikibase_item"
        #         },
        #         "_concat_args_size": 50,
        #         "_continuation_limit": 1000,
        #     },
        #     "schema": {},
        #     "errors": {},
        # })
    ])

    # COMMUNITY_BODY = [
    #     {
    #         "process": "WikipediaRankProcessor.hooks",
    #         "config": {}
    #     }
    # ]
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

    #
    # def finish_pages(self, out, err):
    #     pages = {}
    #     for ind in out.individual_set.all():
    #         if ind.properties["pageid"] not in pages:
    #             pages[ind.properties["pageid"]] = ind
    #             if ind.properties["categories"] is None:
    #                 ind.properties["categories"] = []
    #         else:
    #             if "categories" in ind.properties and ind.properties["categories"]:
    #                 pages[ind.properties["pageid"]].properties["categories"] += ind.properties["categories"]
    #
    #     revisions = self.growth_set.filter(type="revisions").last().output
    #     for page in revisions.individual_set.all():
    #         try:
    #             pages[page.properties["pageid"]].properties.update(page.properties)
    #         except KeyError:
    #             print("KeyError:", page.properties["pageid"])
    #
    #     out.individual_set.all().delete()
    #     out.individual_set.bulk_create(six.itervalues(pages), batch_size=settings.MAX_BATCH_SIZE)

    def set_kernel(self):
        self.kernel = self.current_growth.output

    class Meta:
        verbose_name = "Visual translation"
        verbose_name_plural = "Visual translations"
