import pandas as pd

from future_fashion.colors import get_colors_individual, get_vector_from_colors


class ClothingFrame(object):

    def __init__(self, individuals=None, file_path=None, num_colors=2):
        assert individuals or file_path, "ClothingFrame needs either individuals or a file path"
        self.num_colors = num_colors
        self.frame = None
        if individuals:
            self.load_individuals(individuals)
        else:
            self.from_disk(file_path)

    def load_individuals(self, individuals):
        records = []
        for ind in individuals:
            colors = get_colors_individual(ind.properties, num_colors=self.num_colors, space="rgb")
            if not colors:
                continue
            vector = get_vector_from_colors(colors)
            records.append([ind.id] + vector + [ind["type"]])
        labels = ["ix"]
        labels += self.get_color_columns()
        labels += ["type"]
        self.frame = pd.DataFrame.from_records(records, index="ix", columns=labels).dropna(axis=0)

    def to_disk(self, file_path):
        self.frame.to_pickle(file_path)

    def from_disk(self, path):
        self.frame = pd.read_pickle(path)
        columns = len(self.frame.columns)
        color_columns = columns - 1  # type is the only additional column besides colors for now
        self.num_colors = int(color_columns / 3)

    def get_color_columns(self):
        columns = []
        for num in range(self.num_colors):
            num = str(num)
            columns += ["r"+num, "g"+num, "b"+num]
        return columns

    def get_colors_frame(self, clothing_type=None):
        frame = self.frame[self.frame["type"] == clothing_type] if clothing_type else self.frame
        return frame[self.get_color_columns()]

    def get_type_series(self):
        return self.frame["type"]
