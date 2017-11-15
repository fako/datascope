from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="RedditScrapeCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-d', '--delete', action="store_true")
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
