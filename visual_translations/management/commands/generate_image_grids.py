from __future__ import unicode_literals, absolute_import, print_function, division

from core.management.commands._community import CommunityCommand


class Command(CommunityCommand):

    community_model = "VisualTranslationsEUCommunity"

    def handle_community(self, community, **options):
        community.finish_download(None, None)
