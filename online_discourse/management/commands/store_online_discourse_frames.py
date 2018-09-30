from django.core.management.base import BaseCommand

from core.models.organisms.states import CommunityState
from online_discourse.models import DiscourseSearchCommunity


class Command(BaseCommand):

    def handle(self, *arguments, **options):
        for inst in DiscourseSearchCommunity.objects.filter(state=CommunityState.READY):
            inst.store_frames()
