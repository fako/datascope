import os
import shutil

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from future_fashion.models import InventoryCommunity


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('image', type=str)

    def handle(self, *args, **options):
        image = options["image"]
        # Get inventory and calculate similarity with input
        inventory = InventoryCommunity.objects.last()
        main_colors = inventory.get_main_colors_from_file(image)
        vector = inventory.get_vector_from_colors(main_colors)
        colors_frame = inventory.get_colors_frame()
        similarity = cosine_similarity(colors_frame, np.array(vector).reshape(1, -1)).flatten()
        # Find indices for ten most similar objects and sort by most similar
        indices = np.argsort(similarity)[-10:]
        content = list(inventory.kernel.content)
        matches = [content[ix] for ix in indices]
        matches.reverse()
        # Create directory for input and copy matches there
        basename = os.path.basename(image)
        name, ext = os.path.splitext(basename)
        dest = os.path.join(default_storage.location, "inventory", "colorz", name)
        if not os.path.exists(dest):
            os.makedirs(dest)
        shutil.copy2(image, os.path.join(dest, basename))
        for ix, match in enumerate(matches):
            name, ext = os.path.splitext(match["path"])
            shutil.copy2(match["path"], os.path.join(dest, str(ix) + ext))
