from collections import OrderedDict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from core.processors.base import Processor

from future_fashion.colors import get_vector_from_colors
from future_fashion.frames import ClothingFrame


class ClothingSetMatchProcessor(Processor):

    def __init__(self, config):
        super().__init__(config)
        self.clothing_frame = ClothingFrame(file_path=self.config.clothing_frame_path)

    def color_and_type(self, individuals):
        palette = {
            key[1:]: [int(value) for value in rgb.split(",")]
            for key, rgb in self.config.to_dict().items() if key.startswith("$")
        }

        # Get indexes of color matches per clothing type
        indices = OrderedDict()
        for clothing_type in palette.keys():
            colors = self._get_colors_from_palette(palette, clothing_type)
            frame = self.clothing_frame.get_colors_frame(clothing_type)
            for index in self._get_prominent_color_match_indices(colors, frame)[:self.config.type_limit]:
                indices[index] = None

        for individual in individuals:
            if individual["_id"] in indices:
                indices[individual["_id"]] = individual

        for individual in indices.values():
            yield individual

    @staticmethod
    def _get_colors_from_palette(palette, clothing_type):
        if clothing_type == "top":
            return [palette["top"], palette["bottom"]]
        elif clothing_type == "bottom":
            return [palette["bottom"], palette["top"]]
        else:
            raise ValueError("Unknown clothing type {}".format(clothing_type))

    def _get_prominent_color_match_indices(self, colors, colors_frame):
        vector = get_vector_from_colors(colors)
        for num in range(0, self.clothing_frame.num_colors * 3, 3):
            color_vector = vector[num:num+3]
            color_columns = colors_frame.columns[num:num+3]
            color_similarity = cosine_similarity(
                colors_frame.loc[:,color_columns],
                np.array(color_vector).reshape(1, -1)
            )
            color_similarity = color_similarity.flatten()
            indices = np.argsort(color_similarity)
            cut_ix = next((num for num, ix in enumerate(indices[::-1]) if color_similarity[ix] < 0.99), None)
            if cut_ix is None:
                break
            colors_frame = colors_frame.iloc[indices[-1 * cut_ix:]]
        indices = list(colors_frame.index.values)
        return indices
