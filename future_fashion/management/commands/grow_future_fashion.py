from __future__ import unicode_literals, absolute_import, print_function, division

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="FutureFashionCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})

    def handle_community(self, community, **options):
        community.signature = "tagged_kleding"
        super(Command, self).handle_community(community, **options)
