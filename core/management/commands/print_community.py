from __future__ import unicode_literals, absolute_import, print_function, division

from core.management.commands._community import CommunityCommand


class Command(CommunityCommand):
    """
    Continuously polls a Community until it's completely grown.
    """

    def handle_community(self, community, **options):
        for page in community.manifestation[:10]:
            print("Title:", page["title"])
            print("Categories count:", page.get("categories", []))
            print("Revision count:", page["revisions"])
            print("Rank:", page["ds_rank"])
