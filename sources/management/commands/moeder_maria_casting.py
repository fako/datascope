#from six.moves import range

from django.core.management.base import BaseCommand

from core.processors.resources import HttpResourceProcessor


class Command(BaseCommand):
    """
    Scrapes profiles of actors/actresses from Moeder Maria Casting
    """

    def handle(self, *args, **kwargs):
        SITE_SIZE = 620

        args_list = [[] for i in xrange(SITE_SIZE)]
        kwargs_list = [{"page": i+1} for i in xrange(SITE_SIZE)]
        config = {
            "resource":"MoederAnneCastingSearch",
            "interval_duration": 1000
        }

        hrp = HttpResourceProcessor(config=config)
        task = hrp.fetch_mass.delay(args_list, kwargs_list)

        print "TASK:", task
