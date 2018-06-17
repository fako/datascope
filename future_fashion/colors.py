import itertools
from operator import itemgetter

import pandas as pd
from colorz import colorz


def get_main_colors_from_file(file_path):
    return list(map(itemgetter(0), colorz(file_path)))


def get_vector_from_colors(colors):
    return list(itertools.chain(*colors))


def get_colors_frame(individuals):
    records = [get_vector_from_colors(ind["colors"]) for ind in individuals]
    num_colors = int(len(records[0])/3)
    labels = []
    for ix in range(num_colors):
        ix = str(ix)
        labels += ["r"+ix, "g"+ix, "b"+ix]
    return pd.DataFrame.from_records(records, columns=labels)
