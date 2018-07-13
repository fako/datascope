import itertools
from PIL import Image
from collections import Counter
from colorsys import rgb_to_hsv

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from colorz import DEFAULT_NUM_COLORS, DEFAULT_MINV,DEFAULT_MAXV, THUMB_SIZE
from colorz import get_colors, clamp, order_by_hue


def convert_rgb_to_hsv(rgb):
    hsv = list(rgb_to_hsv(*map(lambda x: x / 256, rgb)))
    hsv[0] = round(hsv[0] * 360)
    hsv[1] = round(hsv[1] * 100)
    hsv[2] = round(hsv[2] * 100)
    return hsv


def extract_dominant_colors(fd, num=DEFAULT_NUM_COLORS, min_v=DEFAULT_MINV, max_v=DEFAULT_MAXV):
    """
    Like the colorz function from the colorz package, but orders by color dominance
    and never returns bold colors
    """
    if not isinstance(fd, Image.Image):
        img = Image.open(fd)
    else:
        img = fd
    img.thumbnail(THUMB_SIZE)

    obs = get_colors(img)
    clamped = [clamp(color, min_v, max_v) for color in obs]
    kmeans = KMeans(n_clusters=num).fit(np.array(clamped).astype(float))
    clusters = kmeans.cluster_centers_
    labels = kmeans.labels_

    total = len(labels)
    counts = Counter(labels)
    colors = [clusters[ix].astype(np.int32).tolist() for ix, count in counts.most_common()]
    balance = [round(count / total * 100) for ix, count in counts.most_common()]

    return colors, balance


def get_vector_from_colors(colors):
    return list(itertools.chain(*colors))


def get_colors_individual(individual, num_colors=None, space=None):
    colors = individual.get("colors", {})
    if not isinstance(colors, dict) or not colors:
        return None
    if num_colors is None:
        return colors
    colors = colors.get(str(num_colors), {})
    if space is None:
        return colors
    return colors.get(space, [])


def create_colors_data(rgb_colors, balance):
    colors = {}
    colors[str(len(rgb_colors))] = {
        "rgb": rgb_colors,
        "hsv": [convert_rgb_to_hsv(color) for color in rgb_colors],
        "balance": balance
    }
    return colors


def get_colors_frame(content, num_colors=3, by_hue=False):
    records = []
    for ix, ind in enumerate(content):
        colors = get_colors_individual(ind, num_colors=num_colors, space="rgb")
        if not colors:
            continue
        if by_hue:
            colors = order_by_hue(colors)
        vector = get_vector_from_colors(colors)
        records.append([ix] + vector)
    num_colors = int(len(records[0])/3)
    labels = ["ix"]
    for num in range(num_colors):
        num = str(num)
        labels += ["r"+num, "g"+num, "b"+num]
    return pd.DataFrame.from_records(records, index="ix", columns=labels).dropna(axis=0)
