from itertools import islice

import pandas as pd

from core.processors.base import Processor


class ClothingSetMatchProcessor(Processor):

    def __init__(self, config):
        super().__init__(config)
        self.color_frame = pd.read_pickle(self.config.color_frame_path)
        print(self.color_frame.shape)

    def color(self, individuals):
        for individual in islice(individuals, 10):
            yield individual
