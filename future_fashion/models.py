from django.core.files.storage import default_storage

from collections import OrderedDict

from core.models.organisms import Community, Collective, Individual


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
                "_continuation_limit": 10
            },
            "schema": {},
            "errors": {},
        })
    ])

    COMMUNITY_BODY = []

    ASYNC_MANIFEST = True
    INPUT_THROUGH_PATH = False

    PUBLIC_CONFIG = {}

    def initial_input(self, *args):
        collective = Collective.objects.create(community=self, schema={})
        for target_listing in TARGET_LISTINGS[:1]:
            Individual.objects.create(
                community=self,
                collective=collective,
                schema={},
                properties={
                    "listing": target_listing
                }
            )
        return collective

    def set_kernel(self):
        self.kernel = self.current_growth.output

    @property
    def manifestation(self):
        return list(super(FutureFashionCommunity, self).manifestation)[:20]

    class Meta:
        verbose_name = "Future fashion"
        verbose_name_plural = "Future fashions"
