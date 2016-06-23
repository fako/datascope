from __future__ import unicode_literals, absolute_import, print_function, division

from scipy.spatial.distance import euclidean

from core.processors.compare import ComparisonProcessor


class ImageFeaturesCompareProcessor(ComparisonProcessor):

    @staticmethod
    def euclidean_distance(individual, reference_individual):
        distance = euclidean(individual["vectors"], reference_individual["vectors"])
        return distance
