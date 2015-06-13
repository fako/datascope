from __future__ import unicode_literals, absolute_import, print_function, division

from core.processors.rank import RankProcessor


class WikipediaRankProcessor(RankProcessor):

    @staticmethod
    def revision_count(page):
        return len(page.get("revisions", []))

    @staticmethod
    def category_count(page):
        return len(page.get("categories", []))