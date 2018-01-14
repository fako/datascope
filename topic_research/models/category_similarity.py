# TODO: fix GH-82 to make the Category similarity work and GH-83 to make it useful

from itertools import islice
from collections import OrderedDict

from core.models.organisms import Community, Collective, Individual


class WikipediaCategorySimularityCommunity(Community):

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
                    "categories": "$.categories",
                },
                "_update_key": "title"
            },
            "schema": {},
            "errors": {
                300: "ambiguous",
                404: "not_found"
            },
        }),
        ("categories", {
            "process": "HttpResourceProcessor.fetch",
            "input": "@search",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.title"],
                "_kwargs": {},
                "_resource": "WikipediaCategories",
                "_objective": {
                    "@": "$.query.pages",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "size": "$.categoryinfo.size"
                },
                "_continuation_limit": 10
            },
            "schema": {},
            "errors": {},
        }),
        ("category_members", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@categories",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective#pageid",
            "config": {
                "_args": ["$.title"],
                "_kwargs": {},
                "_resource": "WikipediaCategoryMembers",
                "_objective": {
                    "@": "$.query.pages",
                    "pageid": "$.pageid",
                    "title": "$.title",
                    "wikidata": "$.pageprops.wikibase_item",
                    "image": "$.pageprops.page_image_free",
                    "categories": "$.categories",
                },
                "_continuation_limit": 10
            },
            "schema": {},
            "errors": {},
        })
    ])

    COMMUNITY_BODY = [
        {
            "name": "compare_categories",
            "process": "WikipediaCompareProcessor.hooks",
            "config": {}
        }
    ]

    PUBLIC_CONFIG = {
        "$categories": 1
    }

    def initial_input(self, *args):
        return Individual.objects.create(community=self, schema={}, properties={
            "title": args[0]
        })

    def error_search_ambiguous(self, errors, out):
        return False

    def error_search_not_found(self, errors, out):
        return False

    def finish_search(self, out, err):
        out["category_titles"] = [
            category["title"] for category in out["categories"]
        ]
        out.save()

    def finish_categories(self, out, err):
        for category in out.individual_set.all().iterator():
            title = category["title"].lower()
            if "people" in title:
                category.delete()
            if "deaths" in title:
                category.delete()
            if "births" in title:
                category.delete()

    def finish_category_members(self, out, err):
        filtered = Collective.objects.create(
            community=self,
            schema=out.schema
        )
        buffer = []
        buffer_size = 500
        current = None

        for member in out.individual_set.all().order_by("identity").iterator():
            if current is None:  # initializing
                current = member
                if not current["categories"]:
                    current["categories"] = []
            elif current.identity != member.identity:  # new group
                buffer.append(current)
                if len(buffer) >= buffer_size:
                    filtered.update(buffer, batch_size=buffer_size, reset=False)
                    buffer = []
                current = member
                if not current["categories"]:
                    current["categories"] = []
            elif current.identity == member.identity:  # same group
                if member["categories"]:
                    categories = current["categories"] + member["categories"]
                    current["categories"] = [
                        individual for index, individual in enumerate(categories)
                        if individual not in categories[index + 1:]
                    ]
        else:
            buffer.append(current)
            filtered.update(buffer, batch_size=buffer_size, reset=False)

        self.current_growth.output = filtered
        self.current_growth.save()

    def before_compare_categories_manifestation(self, manifestation_part):
        subject = self.get_growth("search").input
        self.config = {"_reference": subject.id}

    def set_kernel(self):
        self.kernel = self.get_growth("category_members").output

    @property
    def manifestation(self):
        return islice(super(WikipediaCategorySimularityCommunity, self).manifestation, 1, 21)

    class Meta:
        verbose_name = "Wikipedia category similarity"
        verbose_name_plural = "Wikipedia categories similarities"
