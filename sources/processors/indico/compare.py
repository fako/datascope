from __future__ import unicode_literals, absolute_import, print_function, division

from scipy.spatial.distance import euclidean

from core.processors.compare import ComparisonProcessor


class ImageFeatureProcessor(ComparisonProcessor):

    @staticmethod
    def euclidian_distance(individual, reference_individual):
        return euclidean(individual["vectors"], reference_individual["vectors"])
