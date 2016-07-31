from __future__ import unicode_literals, absolute_import, print_function, division

from core.processors.compare import ComparisonProcessor


class ImageFeaturesCompareProcessor(ComparisonProcessor):

    @staticmethod
    def euclidean_distance(individual, reference_individual):
        from scipy.spatial.distance import euclidean
        distance = euclidean(individual["vectors"], reference_individual["vectors"])
        if not distance:
            return 0.99999999
        else:
            return 1/distance
