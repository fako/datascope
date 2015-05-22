#from six.moves import range

from django.core.management.base import BaseCommand

from core.processors.resources import HttpResourceProcessor
from sources.models.websites.moederannecasting import MoederAnneCastingSearch


class Command(BaseCommand):
    """
    Commands to work with Moeder Anne Casting website.
    """

    SITE_SIZE = 620

    def fetch(self):
        """
        Scrapes profiles of actors/actresses from Moeder Maria Casting
        """
        args_list = [[] for i in xrange(self.SITE_SIZE)]
        kwargs_list = [{"page": i+1} for i in xrange(self.SITE_SIZE)]
        config = {
            "resource":"MoederAnneCastingSearch",
            "interval_duration": 1000
        }

        hrp = HttpResourceProcessor(config=config)
        task = hrp.fetch_mass.delay(args_list, kwargs_list)

        print "TASK:", task

    def handle(self, *args, **kwargs):
        for link in MoederAnneCastingSearch.objects.all()[:1]:
            content_type, data = link.content
            print content_type
