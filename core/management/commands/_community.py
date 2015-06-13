from __future__ import unicode_literals, absolute_import, print_function, division

from datetime import datetime

from django.core.management.base import BaseCommand

from core.utils.helpers import get_any_model
from core.utils.configuration import DecodeConfigAction


class CommunityCommand(BaseCommand):
    """
    Base command for Community centered commands
    """

    def add_arguments(self, parser):
        parser.add_argument('community', type=unicode)
        parser.add_argument('-a', '--args', type=unicode, nargs="*", default="")
        parser.add_argument('-c', '--config', type=unicode, action=DecodeConfigAction, nargs="?", default={})

    def handle_community(self, community, **options):
        raise NotImplementedError("You should implement the handle_community method.")

    def handle(self, *args, **options):
        Community = get_any_model(options.pop("community"))
        community, created = Community.get_or_create_by_input(*args, **options["config"])
        print("Start:", datetime.now())
        self.handle_community(community, **options)
        print("End:", datetime.now())
