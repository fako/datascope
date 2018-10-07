from tqdm import tqdm

from django.core.management.base import BaseCommand

from core.models.organisms.states import CommunityState
from online_discourse.models import DiscourseSearchCommunity


class Command(BaseCommand):

    def handle(self, *arguments, **options):
        queryset = DiscourseSearchCommunity.objects.filter(state=CommunityState.READY)
        for inst in tqdm(list(queryset)):
            inst.store_frames()
