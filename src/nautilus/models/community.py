from collections import OrderedDict
from decimal import Decimal
from math import ceil

from django.conf import settings

from core.models.organisms import Community

from nautilus.locafora import get_product


class LocaforaOrderOverviewCommunity(object):

    COMMUNITY_SPIRIT = OrderedDict([
        ("orders", {
            "process": "HttpPrivateResourceProcessor.fetch",
            "input": "Individual",
            "contribute": "Append:ExtractProcessor.extract_from_resource",
            "output": "Collective",
            "config": {
                "_args": [],
                "_kwargs": {},
                "_resource": "nautilus.LocaforaOrders",
                "_objective": {
                    "@": "$.data",
                    "first_name": "$.payer_first_name",
                    "last_name": "$.payer_last_name",
                    "orders": "$.order_shop_products"
                },
                "_auth": {
                    "resource": "nautilus.LocaforaLogin",
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

    COMMUNITY_BODY = []

    def finish_orders(self, out, err):
        for customer in out.documents.all():
            clean_order_lines = []
            for order_line in customer.properties["orders"].values():
                quantity = int(ceil(float(order_line["quantity"])))
                if quantity == 0:
                    continue
                price = Decimal(order_line["price"]).quantize(Decimal('.01'))
                clean_order_lines.append({
                    "customer": customer.properties["first_name"].strip(),
                    "quantity": quantity,
                    "product": get_product(order_line["title"]),
                    "price": price,
                    "total": price * quantity,
                    "unit": order_line["unit"]
                })
            customer.properties["order_lines"] = clean_order_lines
            customer.save()

    def set_kernel(self):
        self.kernel = self.current_growth.output

    class Meta:
        verbose_name = "Locafora order overview community"
        verbose_name_plural = "Locafora order overview communities"
