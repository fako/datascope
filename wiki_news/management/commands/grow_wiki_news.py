from __future__ import unicode_literals, absolute_import, print_function, division

from datetime import date, datetime, timedelta

from core.management.commands.grow_community import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction
from sources.models.wikipedia import WikipediaListPages, WikipediaRecentChanges, WikiDataItems
from wiki_news.models import WikiNewsCommunity

class Command(GrowCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default="WikiNewsCommunity")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-d', '--delete', action="store_true")

    @staticmethod
    def clear_database():
        three_days_ago = datetime.now() - timedelta(days=3)
        WikiNewsCommunity.objects.filter(created_at__lte=three_days_ago).delete()
        WikipediaRecentChanges.objects.all().delete()
        WikipediaListPages.objects.all().delete()
        WikiDataItems.objects.all().delete()

    @staticmethod
    def archive_growth():
        for community in WikiNewsCommunity.objects.filter(signature="latest-news"):
            start = datetime.fromtimestamp(community.config.start_time)
            end = datetime.fromtimestamp(community.config.end_time)
            community.signature = "from:{}-till:{}".format(
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d")
            )
            community.save()
            community.manifestation_set.all().delete()

    def handle_community(self, community, **options):
        today_at_midnight = (date.today() - date(1970, 1, 1)).total_seconds()
        yesterday_at_midnight = today_at_midnight - 60 * 60 * 24
        community.config = {
            "start_time": yesterday_at_midnight,
            "end_time": today_at_midnight
        }
        community.signature = "latest-news"
        super(Command, self).handle_community(community, **options)

    def handle(self, *args, **options):
        if options["delete"]:
            self.clear_database()
        self.archive_growth()
        super(Command, self).handle(*args, **options)
