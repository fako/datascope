from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction
from sources.models import WikipediaTransclusions, WikipediaRevisions
from wiki_feed.models import WikiFeedPublishCommunity


class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="WikiFeedPublishCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-d', '--delete', action="store_true")

    @staticmethod
    def clear_database():
        WikiFeedPublishCommunity.objects.all().delete()
        WikipediaTransclusions.objects.all().delete()
        WikipediaRevisions.objects.all().delete()

    def get_community(self):
        return self.model.objects.create_by_signature(self.signature, **self.config)

    def handle(self, *args, **options):
        if options["delete"]:
            self.clear_database()
        super(Command, self).handle(*args, **options)
