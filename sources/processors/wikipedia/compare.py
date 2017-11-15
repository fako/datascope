from __future__ import unicode_literals, absolute_import, print_function, division

from core.processors.compare import ComparisonProcessor


class WikipediaCompareProcessor(ComparisonProcessor):

    @staticmethod
    def categories(individual, reference_individual):
        return len([
            category for category in individual["categories"]
            if category["title"] in reference_individual["category_titles"]
        ])
