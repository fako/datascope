from core.management.commands import CommunityCommand


class Command(CommunityCommand):
    """
    Deletes a community by signature
    """

    def handle_community(self, community, *args, **options):
        community.delete()
        print("Community deleted with signature: " + self.signature)
