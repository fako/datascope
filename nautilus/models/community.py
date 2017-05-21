from collections import OrderedDict

from django.conf import settings

from core.models.organisms import Community


class LocaforaOrderOverviewCommunity(Community):

    COMMUNITY_SPIRIT = OrderedDict([
        ("orders", {
            "process": "HttpPrivateResourceProcessor.fetch",
            "input": "Individual",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": [],
                "_kwargs": {},
                "_resource": "LocaforaOrders",
                "_objective": {
                    "@": "$.data",
                    "first_name": "$.payer_first_name",
                    "last_name": "$.payer_last_name",
                    "orders": "$.shop.order_shop_products"
                },
                "_auth": {
                    "resource": "LocaforaLogin",
                    "credentials": {
                        "email": "email@fakoberkers.nl",
                        "password": getattr(settings, 'LOCAFORA_PASSWORD', '')
                    }
                }
            },
            "schema": {},
            "errors": {},
        }),
    ])

    COMMUNITY_BODY = [
        # {
        #     "process": "ManifestProcessor.manifest_from_individuals",
        #     "config": {
        #         "community": "WikiFeedCommunity",
        #         "args": ["$.feed.source"],
        #         "kwargs": "$.feed.modules"
        #     }
        # }
    ]

    def finish_orders(self, out, err):
        for customer in out.individual_set.all():
            pass


    def set_kernel(self):
        self.kernel = self.current_growth.output

    class Meta:
        verbose_name = "Locafora order overview community"
        verbose_name_plural = "Locafora order overview communities"
