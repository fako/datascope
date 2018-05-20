import os
from collections import OrderedDict
from itertools import islice

import pandas as pd

from django.core.files.storage import default_storage

from core.models.organisms import Community, Collective, Individual
from sources.models.downloads import ImageDownload, ImageDownloadSorter


TARGET_LISTINGS = [
    "/dames/kleding/jassen/",
    "/dames/kleding/jurken/",
    "/dames/kleding/truien-vesten/",
    "/dames/kleding/broeken-jeans/",
    "/dames/kleding/blouses-tunieken/",
    "/dames/kleding/tops-shirts/",
    "/dames/kleding/rokken/",
    "/dames/kleding/jumpsuits/",
    "/dames/kleding/lingerie-ondermode/",
    "/dames/kleding/nachtmode/",
    "/dames/schoenen/laarzen/",
    "/dames/schoenen/sneakers/",
    "/dames/schoenen/pumps/",
    "/dames/schoenen/veterschoenen/",
    "/dames/schoenen/ballerinas/",
    "/dames/schoenen/lage-schoenen/",
    "/dames/schoenen/instappers/",
    "/dames/schoenen/pantoffels/",
    "/dames/schoenen/sleehakken/",
    "/dames/schoenen/outdoorschoenen/",
    "/dames/sport-badmode/sportmode/",
    "/dames/sport-badmode/skikleding/",
    "/dames/sport-badmode/regenkleding/",
    "/dames/accessoires/sjaals/",
    "/dames/accessoires/hoeden-mutsen/",
    "/dames/accessoires/handschoenen/",
    "/dames/tassen/clutches/",
    "/dames/tassen/handtassen/",
    "/dames/tassen/schoudertassen/",
    "/dames/sieraden/armbanden/",
    "/dames/sieraden/horloges/",
    "/dames/sieraden/kettingen/",
    "/dames/sieraden/ringen/",
    "/heren/kleding/jassen/",
    "/heren/kleding/overhemden/",
    "/heren/kleding/truien-vesten/",
    "/heren/kleding/broeken-jeans/",
    "/heren/kleding/tops-shirts/",
    "/heren/kleding/pakken/",
    "/heren/kleding/lingerie-ondermode/",
    "/heren/kleding/nachtmode/",
    "/heren/schoenen/laarzen/",
    "/heren/schoenen/sneakers/",
    "/heren/schoenen/klassieke-schoenen/",
    "/heren/schoenen/veterschoenen/",
    "/heren/schoenen/lage-schoenen/",
    "/heren/schoenen/instappers/",
    "/heren/schoenen/pantoffels/",
    "/heren/schoenen/outdoorschoenen/",
    "/heren/accessoires/sjaals/",
    "/heren/accessoires/hoeden-mutsen/",
    "/heren/accessoires/handschoenen/",
    "/heren/accessoires/dassen-pochetten/",
    "/heren/accessoires/riemen-bretels/",
    "/heren/sport-badmode/regenkleding/",
    "/heren/sport-badmode/skikleding/",
    "/heren/sport-badmode/sportmode/",
    "/heren/sport-badmode/sportmode/schoenen/",
    "/jongens/kleding/jassen/",
    "/jongens/kleding/truien-vesten/",
    "/jongens/kleding/overhemden/",
    "/jongens/kleding/broeken-jeans/",
    "/jongens/schoenen/sneakers/",
    "/jongens/schoenen/laarzen/",
    "/jongens/accessoires/sjaals/",
    "/jongens/accessoires/handschoenen/",
    "/jongens/accessoires/hoeden-mutsen/",
    "/meisjes/kleding/jassen/",
    "/meisjes/kleding/jurken/",
    "/meisjes/kleding/truien-vesten/",
    "/meisjes/kleding/rokken/",
    "/meisjes/kleding/blouses-tunieken/",
    "/meisjes/schoenen/laarzen/",
    "/meisjes/schoenen/sneakers/",
    "/meisjes/accessoires/sjaals/",
    "/meisjes/accessoires/handschoenen/",
    "/baby/kleding/jassen/",
    "/baby/kleding/truien-vesten/",
    "/baby/kleding/broeken-jeans/",
    "/baby/kleding/tops-shirts/",
    "/baby/kleding/lingerie-ondermode/rompertjes/",
    "/baby/accessoires/hoeden-mutsen/",
    "/baby/accessoires/sjaals/",
    "/baby/schoenen/laarzen/",
    "/baby/schoenen/sneakers/"
]


class FutureFashionCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("items", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": None,
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": ["$.listing"],
                "_kwargs": {},
                "_objective": {
                    "@": " [el for el in soup.find_all(class_='item') if len(el['class']) == 1]",
                    "#canon": "soup.find(attrs={'rel':'canonical'}).get('href')",
                    "#tags": "soup.find(attrs={'rel':'canonical'}).get('href').replace('https://www.kleding.nl/', '').split('/')[:-1]",
                    "details": "next(iter(el.find_all('a')), {}).get('href', '')",
                    "image": "next(iter(el.select('.image img')), {}).get('src', '')",
                    "shop": "el.find(class_='shop').get_text() if el.find(class_='shop') else ''",
                    "price": "el.find(class_='current').get_text() if el.find(class_='current') else ''",
                    "product": "el.find(class_='title').get_text() if el.find(class_='title') else ''",
                    "brand": "el.find(class_='brand').get_text() if el.find(class_='brand') else ''",
                },
                "_resource": "KledingListing",
                "_continuation_limit": 100,
                "_interval_duration": 1000
            },
            "schema": {},
            "errors": {},
        }),
        ("download", {
            "process": "HttpResourceProcessor.fetch_mass",
            "input": "@items",
            "contribute": None,
            "output": None,
            "config": {
                "_args": ["$.image"],
                "_kwargs": {},
                "_resource": "ImageDownload",
                "_interval_duration": 100
            },
            "schema": {},
            "errors": None,
        })
    ])

    COMMUNITY_BODY = []

    ASYNC_MANIFEST = False
    INPUT_THROUGH_PATH = False

    PUBLIC_CONFIG = {}

    def initial_input(self, *args):
        collective = Collective.objects.create(community=self, schema={})
        for target_listing in TARGET_LISTINGS:
            Individual.objects.create(
                community=self,
                collective=collective,
                schema={},
                properties={
                    "listing": target_listing
                }
            )
        return collective

    def finish_download(self, out, err):
        items_growth = self.get_growth("items")
        self.sort_downloads_by_tags(items_growth.output)

    def sort_downloads_by_tags(self, collective):
        train, validate, test = collective.split(as_content=True)
        for data_type, data_set in [("train", train), ("validate", validate), ("test", test)]:
            sorter = ImageDownloadSorter(
                source_base=default_storage.location,
                destination_base=os.path.join(default_storage.location, self.signature, data_type),
                url_key="image",
                destination_lambda=lambda file_: os.path.join(file_["tags"][0], file_["tags"][1])
            )
            sorter(data_set)

    def sort_downloads_by_brand(self, collective):
        # Updates the collective to be identified through "brand"
        if collective.identifier != "brand":
            collective.identifier = "brand"
            collective.save()
            collective.update(collective.individual_set.iterator(), validate=False, reset=False)
        # Calculate which brands are significant to train on
        df = pd.DataFrame.from_records(collective.content)
        brand_counts = df["brand"].value_counts()
        brands = [brand for brand, count in brand_counts.items() if count >= 300 and brand]
        # Split data and sort files by type and brand
        train, validate, test = collective.split(
            query_set=collective.individual_set.filter(identity__in=brands),
            as_content=True
        )
        for data_type, data_set in [("train", train), ("validate", validate), ("test", test)]:
            sorter = ImageDownloadSorter(
                source_base=default_storage.location,
                destination_base=os.path.join(default_storage.location, self.signature, data_type),
                url_key="image",
                destination_lambda=lambda file_: file_["brand"]
            )
            sorter(data_set)

    def set_kernel(self):
        self.kernel = self.growth_set.filter(type="items").last().output

    @property
    def manifestation(self):
        return islice(super(FutureFashionCommunity, self).manifestation, 0, 20)

    class Meta:
        verbose_name = "Future fashion"
        verbose_name_plural = "Future fashions"
