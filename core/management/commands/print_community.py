from pprint import pprint
import logging
from json import dumps

from core.management.commands._community import CommunityCommand
from core.utils.configuration import DecodeConfigAction


class Command(CommunityCommand):
    """
    Continuously polls a Community until it's completely grown.
    """
    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('--kernel-content', action="store_true")
        parser.add_argument('--limit', type=int, default=None)
        parser.add_argument('--indent', type=int, default=None)

    def handle_community(self, community, *arguments, **options):
        output = community.kernel.content if options["kernel_content"] else community.manifestation
        print(dumps(list(output)[:options["limit"]], indent=options["indent"]))

    def handle(self, *args, **options):
        logging.disable(logging.INFO)
        super(Command, self).handle(*args, **options)
