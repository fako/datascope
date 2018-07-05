import os
import shutil
import logging
import json
from PIL import Image

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from django.core.files.storage import default_storage

from core.management.commands import CommunityCommand
from core.utils.configuration import DecodeConfigAction
from sources.models import ImageDownload
from future_fashion.colors import (extract_dominant_colors, get_vector_from_colors, get_colors_frame,
                                   get_colors_individual)


log = logging.getLogger("datascope")


class Command(CommunityCommand):
    """
    Example: ./manage.py match_face_colors InventoryCommunity -f fako_01 -a multi-color-sklearn
    """

    def add_arguments(self, parser):
        parser.add_argument('community', type=str, nargs="?", default=self.community_model)
        parser.add_argument('-a', '--args', type=str, nargs="*", default="")
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})
        parser.add_argument('-f', '--face', type=str, required=True)
        parser.add_argument('-n', '--number-colors', type=int, default=2)

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

    def get_pupil_image(self, face_image, eye_target, landmarks):
        assert eye_target in ["LEFT_EYE", "RIGHT_EYE"], "Invalid eye_target"
        left_eye_data = {
            landmark["type"]: landmark["position"]
            for landmark in landmarks if eye_target + "_" in landmark["type"]
        }
        eye_left = round(left_eye_data[eye_target + "_LEFT_CORNER"]["x"])
        eye_top = round(left_eye_data[eye_target + "_TOP_BOUNDARY"]["y"])
        eye_right = left_eye_data[eye_target + "_RIGHT_CORNER"]["x"]
        eye_bottom = round(left_eye_data[eye_target + "_BOTTOM_BOUNDARY"]["y"])
        eye_width = eye_right - eye_left
        eye_height = eye_bottom - eye_top
        pupil_half_width = round(eye_width / 6)
        pupil_half_height = round(eye_height / 3)
        pupil_center = round(left_eye_data[eye_target + "_PUPIL"]["x"])
        return face_image.crop(
            (pupil_center - pupil_half_width,
             eye_top + pupil_half_height,
             pupil_center + pupil_half_width,
             eye_bottom - pupil_half_height)
        )

    def handle_community(self, community, *args, **options):
        # Read input
        face = options["face"]
        num_colors = options["number_colors"]
        # Retrieve left pupil from face
        face_dir = os.path.join(default_storage.location, "face_detection", face)
        face_data_file_name = face + ".json"
        try:
            face_image_file_name = face + ".jpg"
            face_image = Image.open(os.path.join(face_dir, face_image_file_name))
        except FileNotFoundError:
            face_image_file_name = face + ".png"
            face_image = Image.open(os.path.join(face_dir, face_image_file_name))
        with open(os.path.join(face_dir, face_data_file_name)) as data_file:
            face_data = json.load(data_file)
        landmarks = face_data["responses"][0]["faceAnnotations"][0]["landmarks"]
        left_pupil = self.get_pupil_image(face_image, "LEFT_EYE", landmarks)
        left_pupil.save(os.path.join(face_dir, "left_pupil.png"))
        right_pupil = self.get_pupil_image(face_image, "RIGHT_EYE", landmarks)
        right_pupil.save(os.path.join(face_dir, "right_pupil.png"))
        # Determine eye color
        left_colors, left_balance = extract_dominant_colors(left_pupil, num=num_colors)
        right_colors, right_balance = extract_dominant_colors(right_pupil, num=num_colors)
        left_vector = get_vector_from_colors(left_colors)
        # Get colors from community data and calculate similarities
        # This loads all data into memory
        content = list(community.kernel.content)
        colors_frame = get_colors_frame(content, num_colors=num_colors)
        log.info("Color frame shape: {}".format(colors_frame.shape))
        similarity = cosine_similarity(colors_frame, np.array(left_vector).reshape(1, -1)).flatten()
        # Find indices for ten most similar objects and sort by most similar
        indices = np.argsort(similarity)[-10:]
        matches = [(similarity[ix], content[ix],) for ix in indices]
        matches.reverse()
        # Create directory for matches
        dest = os.path.join(face_dir, "left_eye")
        if not os.path.exists(dest):
            os.makedirs(dest, exist_ok=True)
        color_data = {
            "input": {
                "left": {
                    "colors": [
                        "#{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in left_colors
                    ],
                    "links": [
                        "http://www.color-hex.com/color/{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in left_colors
                    ]
                },
                "right": {
                    "colors": [
                        "#{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in right_colors
                    ],
                    "links": [
                        "http://www.color-hex.com/color/{0:02x}{1:02x}{2:02x}".format(color[0], color[1], color[2])
                        for color in right_colors
                    ]
                }
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
        with open(os.path.join(face_dir, "eye_colors.js"), "w") as jf:
            json.dump(color_data, jf, indent=4)
        if community.get_name() == "fashion_data":
            self.handle_data_matches(matches, dest)
        else:
            self.handle_inventory_matches(matches, dest)


"""
Example request for the Face Detection API from Google
{
  "requests": [
    {
      "image": {
        "source": {
          "imageUri": "https://yt3.ggpht.com/a-/AJLlDp0_TonmCC9rTR2-Mmg_TsM3k2pY8FOcww3v_w=s900-mo-c-c0xffffffff-rj-k-no"
        }
      },
      "features": [
        {
          "type": "FACE_DETECTION"
        }
      ]
    }
  ]
}
"""
