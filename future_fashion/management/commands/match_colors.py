import os
import shutil
import logging

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from django.core.files.storage import default_storage

from core.management.commands import CommunityCommand
from core.utils.configuration import DecodeConfigAction
from sources.models import ImageDownload
from future_fashion.colors import get_main_colors_from_file, get_vector_from_colors, get_colors_frame


log = logging.getLogger("datascope")


class Command(CommunityCommand):
    """
    Example: ./manage.py match_colors FutureFashionCommunity -i ~/Downloads/fairy-tale.jpg -a tagged_kleding
    """

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-i', '--image', type=str)

    def handle_inventory_matches(self, matches, destination):
        for ix, match_info in enumerate(matches):
            similarity, match = match_info
            name, ext = os.path.splitext(match["path"])
            shutil.copy2(
                match["path"],
                os.path.join(destination, str(ix) + "-" + str(round(similarity, ndigits=3)) + ext)
            )

    def handle_data_matches(self, matches, destination):
        for ix, match_info in enumerate(matches):
            similarity, match = match_info
            uri = ImageDownload.uri_from_url(match["image"])
            try:
                download = ImageDownload.objects.get(uri=uri)
            except ImageDownload.DoesNotExist:
                continue
            if not download.success:
                continue
            name, ext = os.path.splitext(download.body)
            shutil.copy2(
                os.path.join(default_storage.location, download.body),
                os.path.join(destination, str(ix) + "-" + str(round(similarity, ndigits=3)) + ext)
            )

    def handle_community(self, community, *args, **options):
        # Get colors from input file
        image = options["image"]
        main_colors = get_main_colors_from_file(image)
        vector = get_vector_from_colors(main_colors)
        # Get colors from community data and calculate similarities
        # This loads all data into memory
        content = list(community.kernel.content)
        colors_frame = get_colors_frame(content)
        log.info("Color frame shape: {}".format(colors_frame.shape))
        similarity = cosine_similarity(colors_frame, np.array(vector).reshape(1, -1)).flatten()
        # Find indices for ten most similar objects and sort by most similar
        indices = np.argsort(similarity)[-10:]
        matches = [(similarity[ix], content[ix],) for ix in indices]
        matches.reverse()
        # Create directory for input and copy matches there
        basename = os.path.basename(image)
        name, ext = os.path.splitext(basename)
        dest = os.path.join(default_storage.location, community.get_name(), "colorz", name)
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)
        shutil.copy2(image, os.path.join(dest, basename))
        if community.get_name() == "fashion_data":
            self.handle_data_matches(matches, dest)
        else:
            self.handle_inventory_matches(matches, dest)
