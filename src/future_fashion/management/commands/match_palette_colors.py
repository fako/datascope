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
from future_fashion.colors import get_vector_from_colors, get_colors_frame, get_colors_individual


log = logging.getLogger("datascope")


class Command(CommunityCommand):
    """
    Examples:
        ./manage.py match_palette_colors ClothingInventoryCommunity -a 16-07-18 -p "top=228,85,52&bottom=108,25,63&accessories=164,192,217" -t little-french-dress
        ./manage.py match_palette_colors ClothingInventoryCommunity -a 16-07-18 -p "top=241,166,101&bottom=50,93,142&accessories=179,111,114" -t fading-sunshine
        ./manage.py match_palette_colors ClothingInventoryCommunity -a 16-07-18 -p "top=217,163,214&bottom=167,142,191&accessories=197,185,211" -t dozing-off-now
    """

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-t', '--title', type=str)
        parser.add_argument('-p', '--palette', type=str, action=DecodeConfigAction)

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
        for num in range(0, num_colors * 3, 3):
            color_vector = vector[num:num+3]
            color_columns = colors_frame.columns[num:num+3]
            color_similarity = cosine_similarity(colors_frame.loc[:,color_columns], np.array(color_vector).reshape(1, -1)).flatten()
            indices = np.argsort(color_similarity)
            cut_ix = next((num for num, ix in enumerate(indices[::-1]) if color_similarity[ix] < 0.99), None)
            if cut_ix is None:
                log.info("Terminating match at color: {}".format(num % 3))
                break
            colors_frame = colors_frame.iloc[indices[-1 * cut_ix:]]
        else:
            log.info("Taking all {} colors into account".format(num_colors))
        indices = list(colors_frame.index.values)
        matches = [(prio, content[ix],) for prio, ix in enumerate(indices)]
        return matches

    @staticmethod
    def get_colors_from_palette(palette, clothing_type):
        if clothing_type == "top":
            return [palette["top"], palette["accessories"], palette["bottom"]]
        elif clothing_type == "bottom":
            return [palette["bottom"], palette["accessories"], palette["top"]]
        elif clothing_type == "accessories":
            return [palette["accessories"], palette["top"], palette["bottom"]]
        else:
            raise ValueError("Unknown clothing type {}".format(clothing_type))

    def handle_community(self, community, *args, **options):
        # Read from options and set variables
        title = options["title"]
        palette = {key: list(map(int, value.split(","))) for key, value in options["palette"].items()}
        base_dest = os.path.join(default_storage.location, community.get_name(), "palette", title)
        is_data = community.get_name() == "fashion_data"
        if is_data:
            women_individuals = community.kernel.documents.filter(properties__contains='target_group": "dames')
        else:
            women_individuals = community.kernel.documents

        # Get color matches per clothing type
        for clothing_type in palette.keys():
            colors = Command.get_colors_from_palette(palette, clothing_type)
            type_content = [
                ind.properties
                for ind in women_individuals.filter(properties__contains='type": "' + clothing_type)
            ]
            matches = self.get_prominent_matches(colors, type_content, 3)
            self.save_matches(os.path.join(base_dest, clothing_type), colors, matches[:10], is_data=is_data)

    def save_matches(self, dest, colors, matches, is_data=False):
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)
        color_data = {
            "input": {
                "colors": [
                    "#{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                    for color in colors
                ],
                "links": [
                    "http://www.color-hex.com/color/{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                    for color in colors
                ]
            },
            "output": [
                {
                    "similarity": round(similarity, ndigits=3),
                    "colors": [
                        "#{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in get_colors_individual(match, num_colors=3, space="rgb")
                    ],
                    "links": [
                        "http://www.color-hex.com/color/{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in get_colors_individual(match, num_colors=3, space="rgb")
                    ]
                }
                for similarity, match in matches
            ]
        }
        with open(os.path.join(dest, "colors.js"), "w") as jf:
            json.dump(color_data, jf, indent=4)
        if is_data:
            self.handle_data_matches(matches, dest)
        else:
            self.handle_inventory_matches(matches, dest)
