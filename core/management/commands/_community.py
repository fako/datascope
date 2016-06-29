from __future__ import unicode_literals, absolute_import, print_function, division

from datetime import datetime

from django.core.management.base import BaseCommand

from core.utils.helpers import get_any_model
from core.utils.configuration import DecodeConfigAction


class CommunityCommand(BaseCommand):
    """
    Base command for Community centered commands
    """
    community_model = ""

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})

    def handle_community(self, community, **options):
        raise NotImplementedError("You should implement the handle_community method.")

    def handle(self, *args, **options):
        Community = get_any_model(options.pop("community"))
        signature = Community.get_signature_from_input(*args, **options["config"])
        community, created = Community.objects.get_or_create_by_signature(signature, **options["config"])
        print("Start:", datetime.now())
        self.handle_community(community, *args, **options)
        print("End:", datetime.now())
