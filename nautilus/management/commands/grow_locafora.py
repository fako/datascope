from datetime import datetime

from django.conf import settings

from pandas import DataFrame

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction
from core.utils.helpers import format_datetime

from nautilus.models import LocaforaOrders


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="LocaforaOrderOverviewCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-d', '--delete', action="store_true")

    def handle_community(self, community, **options):
        if options["delete"]:
            LocaforaOrders.objects.all().delete()
        community.signature = format_datetime(datetime.utcnow())
        super(Command, self).handle_community(community, **options)
        result = DataFrame()
        for customer in community.kernel.individual_set.all():
            customer_frame = DataFrame(customer["order_lines"])
            result = result.append(customer_frame, ignore_index=True)
        if result.empty:
            print("No orders to process")
            return
        result.sort_values(["product", "customer"], inplace=True)
        result[["customer", "quantity", "product", "unit"]].to_csv('alfabetische-lijst.csv')
