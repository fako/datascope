from __future__ import unicode_literals, absolute_import, print_function, division

import json

from core.management.commands._community import CommunityCommand
from core.utils.configuration import DecodeConfigAction


class Command(CommunityCommand):

    community_model = "VisualTranslationsEUCommunity"

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-l', '--locale', type=str, nargs="?", default="")
        parser.add_argument('-w', '--word', type=str, nargs="?", default="")

    def handle_community(self, community, *arguments, **options):
        word_encoded = json.dumps(options["word"])
        qs = community.individual_set.filter(properties__contains="word\": {}".format(word_encoded))
        print("Deleting {} individuals".format(qs.count()))
        # for ind in qs:
        #     print(ind.properties)
        qs.delete()
