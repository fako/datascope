import os
import shutil
import logging
import json

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from colorz import order_by_hue

from django.core.files.storage import default_storage

from core.management.commands import CommunityCommand
from core.utils.configuration import DecodeConfigAction
from sources.models import ImageDownload
from future_fashion.colors import (extract_dominant_colors, get_vector_from_colors, get_colors_frame,
                                   get_colors_individual)


log = logging.getLogger("datascope")


class Command(CommunityCommand):
    """
    Example: ./manage.py match_image_colors FutureFashionCommunity -i ~/Downloads/fairy-tale.jpg -a tagged_kleding
    """

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-i', '--image', type=str)
        parser.add_argument('-n', '--number-colors', type=int, default=3)
        parser.add_argument('-s', '--similarity', action='store_true')

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

    def get_similarity_matches(self, colors, content, num_colors):
        colors = order_by_hue(colors)
        vector = get_vector_from_colors(colors)
        colors_frame = get_colors_frame(content, num_colors=num_colors, by_hue=True)
        log.info("Color frame shape: {}".format(colors_frame.shape))
        similarity = cosine_similarity(colors_frame, np.array(vector).reshape(1, -1)).flatten()
        # Find indices for ten most similar objects and sort by most similar
        indices = np.argsort(similarity)[-10:]
        matches = [(similarity[ix], content[ix],) for ix in indices]
        matches.reverse()
        return matches

    def get_prominent_matches(self, colors, content, num_colors):
        vector = get_vector_from_colors(colors)
        colors_frame = get_colors_frame(content, num_colors=num_colors)
        log.info("Color frame shape: {}".format(colors_frame.shape))
        for num in range(0, num_colors):
            color_vector = vector[num:num+3]
            color_columns = colors_frame.columns[num:num+3]
            color_similarity = cosine_similarity(colors_frame.loc[:,color_columns], np.array(color_vector).reshape(1, -1)).flatten()
            indices = np.argsort(color_similarity)
            cut_ix = next((ix for ix, _ in enumerate(indices[::-1]) if color_similarity[ix] < 0.95), None)
            if cut_ix is None:
                log.info("Terminating match at color: {}".format(num))
                break
            colors_frame = colors_frame.iloc[indices[-1 * cut_ix:]]
        else:
            log.info("Taking all {} colors into account".format(num_colors))
        indices = list(colors_frame.index.values)
        matches = [(prio, content[ix],) for prio, ix in enumerate(indices)]
        matches.reverse()
        return matches

    def handle_community(self, community, *args, **options):
        # Read from options
        num_colors = options["number_colors"]
        image = options["image"]
        similarity = options["similarity"]
        # Get colors from input file
        main_colors, balance = extract_dominant_colors(image, num=num_colors)
        # Get colors from community data
        # This loads all data into memory
        content = list(community.kernel.content)
        if similarity:
            matches = self.get_similarity_matches(main_colors, content, num_colors)
        else:
            matches = self.get_prominent_matches(main_colors, content, num_colors)
        # Create directory for input and copy matches there
        basename = os.path.basename(image)
        name, ext = os.path.splitext(basename)
        dest = os.path.join(default_storage.location, community.get_name(), "colorz", name)
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)
        shutil.copy2(image, os.path.join(dest, basename))
        color_data = {
            "input": {
                "colors": [
                    "#{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                    for color in main_colors
                ],
                "links": [
                    "http://www.color-hex.com/color/{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                    for color in main_colors
                ]
            },
            "output": [
                {
                    "similarity": round(similarity, ndigits=3),
                    "colors": [
                        "#{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in get_colors_individual(match, num_colors=num_colors, space="rgb")
                    ],
                    "links": [
                        "http://www.color-hex.com/color/{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in get_colors_individual(match, num_colors=num_colors, space="rgb")
                    ]
                }
                for similarity, match in matches
            ]
        }
        with open(os.path.join(dest, "colors.js"), "w") as jf:
            json.dump(color_data, jf, indent=4)
        if community.get_name() == "fashion_data":
            self.handle_data_matches(matches, dest)
        else:
            self.handle_inventory_matches(matches, dest)
