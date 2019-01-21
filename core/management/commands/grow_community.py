import logging

from core.management.commands import CommunityCommand


log = logging.getLogger("datagrowth.command")


class Command(CommunityCommand):
    """
    Continuously polls a Community until it's completely grown.
    """

    def handle_community(self, community, *args, **options):
        community.config = {"async": False}
        community.save()
        community.grow(*args)
        log.info("Result:", community.kernel)
        log.info("Growth:", [growth.id for growth in community.growth_set.all()])
