import os

from django.core.management.base import BaseCommand

from core.models.organisms.states import CommunityState
from future_fashion.models import InventoryCommunity
from future_fashion.frames import ClothingFrame


class Command(BaseCommand):

    def handle(self, *arguments, **options):
        for inventory in InventoryCommunity.objects.filter(state=CommunityState.READY):
            frame = ClothingFrame(inventory.kernel.individual_set.iterator())
            frame_file = inventory.get_clothing_frame_file()
            tail, head = os.path.split(frame_file)
            if not os.path.exists(tail):
                os.makedirs(tail)
            frame.to_disk(frame_file)
