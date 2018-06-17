import os
import shutil

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from django.core.files.storage import default_storage

from core.management.commands import CommunityCommand
from core.utils.configuration import DecodeConfigAction
from future_fashion.models import InventoryCommunity
from future_fashion.colors import get_main_colors_from_file, get_vector_from_colors, get_colors_frame


class Command(CommunityCommand):

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-i', '--image', type=str)

    def handle_community(self, community, *args, **options):
        # Get colors from input file
        image = options["image"]
        main_colors = get_main_colors_from_file(image)
        vector = get_vector_from_colors(main_colors)
        # Get colors from community data and calculate similarities
        # This loads all data into memory
        content = list(community.kernel.content)
        colors_frame = get_colors_frame(content)
        similarity = cosine_similarity(colors_frame, np.array(vector).reshape(1, -1)).flatten()
        # Find indices for ten most similar objects and sort by most similar
        indices = np.argsort(similarity)[-10:]
        matches = [content[ix] for ix in indices]
        matches.reverse()
        # Create directory for input and copy matches there
        basename = os.path.basename(image)
        name, ext = os.path.splitext(basename)
        dest = os.path.join(default_storage.location, community.get_name(), "colorz", name)
        if not os.path.exists(dest):
            os.makedirs(dest)
        shutil.copy2(image, os.path.join(dest, basename))
        for ix, match in enumerate(matches):
            name, ext = os.path.splitext(match["path"])
            shutil.copy2(match["path"], os.path.join(dest, str(ix) + ext))
