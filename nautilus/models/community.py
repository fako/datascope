from collections import OrderedDict
from decimal import Decimal

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
                    "orders": "$.order_shop_products"
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

    COMMUNITY_BODY = []

    def finish_orders(self, out, err):
        for customer in out.individual_set.all():
            clean_order_lines = []
            for order_line in customer.properties["orders"].values():
                quantity = int(float(order_line["quantity"]))
                if quantity == 0:
                    continue
                price = Decimal(order_line["price"]).quantize(Decimal('.01'))
                if order_line["title"].lower().startswith("bio"):
                    product = " ".join(order_line["title"].split(" ")[1:]).strip()
                else:
                    product = order_line["title"].strip()
                clean_order_lines.append({
                    "customer": customer.properties["first_name"].strip(),
                    "product": product,
                    "price": price,
                    "quantity": quantity,
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
