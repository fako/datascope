from __future__ import unicode_literals, absolute_import, print_function, division

import json

from core.management.commands._community import CommunityCommand


class Command(CommunityCommand):
    """
    Continuously polls a Community until it's completely grown.
    """

    def handle_community(self, community, **options):
        print(json.dumps([[page["title"], len(page["revisions"]), len(page.get("categories", [])), page["ds_rank"]] for page in community.manifestation[:10]], indent=4))
