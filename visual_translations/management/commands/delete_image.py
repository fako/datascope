from __future__ import unicode_literals, absolute_import, print_function, division

from core.management.commands._community import CommunityCommand
from core.utils.configuration import DecodeConfigAction


class Command(CommunityCommand):

    community_model = "VisualTranslationsEUCommunity"

    def add_arguments(self, parser):
        parser.add_argument('community', type=unicode, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=unicode, nargs="*", default="")
        parser.add_argument('-c', '--config', type=unicode, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-s', '--src', type=unicode, nargs="?", default="")

    def handle_community(self, community, **options):
        qs = community.individual_set.filter(properties__contains=options["src"])
        print("Deleting {} individuals".format(qs.count()))
        for ind in qs:
            print(ind.properties)
