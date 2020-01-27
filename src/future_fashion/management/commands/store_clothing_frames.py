import os

from django.core.management.base import BaseCommand

from core.models.organisms.states import CommunityState
from future_fashion.models import ClothingInventoryCommunity
from future_fashion.frames import ClothingFrame


class Command(BaseCommand):

    def handle(self, *arguments, **options):
        for inventory in ClothingInventoryCommunity.objects.filter(state=CommunityState.READY):
            frame = ClothingFrame(inventory.kernel.documents.iterator())
            frame_file = inventory.get_clothing_frame_file()
            tail, head = os.path.split(frame_file)
            if not os.path.exists(tail):
                os.makedirs(tail)
            frame.to_disk(frame_file)
