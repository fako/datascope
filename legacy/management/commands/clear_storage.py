from django.core.management.base import BaseCommand

from legacy.helpers.storage import get_hif_model


class Command(BaseCommand):
    """
    Clears TextStorage and/or ProcessStorage from the database.
    """

    def handle(self, *args, **kwargs):

        if not args:
            args = ['TextStorage', 'ProcessStorage']

        for arg in args:
            model = get_hif_model(arg)
            model.objects.all().delete()
