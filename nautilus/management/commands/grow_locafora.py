from datetime import datetime

from django.conf import settings

from pandas import DataFrame

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction

from nautilus.models import LocaforaOrders


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="LocaforaOrderOverviewCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-d', '--delete', action="store_true")

    def handle_community(self, community, **options):
        if options["delete"]:
            LocaforaOrders.objects.all().delete()
        community.signature = datetime.utcnow().strftime(settings.DATASCOPE_DATETIME_FORMAT)
        super(Command, self).handle_community(community, **options)
        result = DataFrame()
        for customer in community.kernel.individual_set.all():
            customer_frame = DataFrame(customer["order_lines"])
            result = result.append(customer_frame, ignore_index=True)
        if result.empty:
            print("No orders to process")
            return
        result.sort("product", inplace=True)
        result.to_csv('out.csv')