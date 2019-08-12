import logging
import os
from datetime import datetime

from pandas import DataFrame

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction
from core.utils.helpers import format_datetime
from datagrowth import settings as datascope_settings
from datagrowth.utils import get_media_path
from nautilus.models import LocaforaOrders


log = logging.getLogger("datagrowth.command")


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="LocaforaOrderOverviewCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-d', '--debug', action="store_true")

    def handle_community(self, community, **options):
        if not options["debug"]:
            LocaforaOrders.objects.all().delete()
        community.signature = format_datetime(datetime.utcnow())
        super(Command, self).handle_community(community, **options)
        result = DataFrame()
        for customer in community.kernel.documents.all():
            customer_frame = DataFrame(customer["order_lines"])
            result = result.append(customer_frame, ignore_index=True)
        if result.empty:
            log.warning("No orders to process")
            return
        result.sort_values(["product", "customer"], inplace=True)
        csv_file_name = "alfabetische-lijst.csv"
        dst = get_media_path("nautilus", "locafora")
        if not os.path.exists(dst):
            os.makedirs(dst)
        result[["customer", "quantity", "product", "unit"]].to_csv(os.path.join(dst, csv_file_name))
