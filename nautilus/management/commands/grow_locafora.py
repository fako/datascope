from datetime import datetime

from django.conf import settings

from pandas import DataFrame

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="LocaforaOrderOverviewCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})

    def handle_community(self, community, **options):
        community.signature = datetime.utcnow().strftime(settings.DATASCOPE_DATETIME_FORMAT)
        super(Command, self).handle_community(community, **options)
        result = DataFrame()
        for customer in community.kernel.individual_set.all():
            customer_frame = DataFrame(customer["order_lines"])
            result = result.append(customer_frame, ignore_index=True)
        result.sort("product", inplace=True)
        result.to_csv('out.csv')