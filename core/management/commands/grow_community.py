from __future__ import unicode_literals, absolute_import, print_function, division


import time


from core.exceptions import DSProcessUnfinished
from core.management.commands._community import CommunityCommand


class Command(CommunityCommand):
    """
    Continuously polls a Community until it's completely grown.
    """

    def handle_community(self, community, **options):
        done = False
        while not done:
            try:
                done = community.grow()
                if done:
                    print("Result:", community.kernel)
                    print("Growth:", [growth.id for growth in community.growth_set.all()])
            except DSProcessUnfinished:
                time.sleep(5)
                continue

