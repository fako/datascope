from django.test import TestCase

from core.models import Individual
from sources.processors.wikipedia.rank import WikipediaRankProcessor


class TestWikiFeedFeatures(TestCase):

    fixtures = [
        "breaking-news"
    ]

    def test_breaking_news(self):
        breaking_news_page = Individual.objects.get(identity="Q42440670")
        is_breaking_news = WikipediaRankProcessor.breaking_news(
            breaking_news_page.properties,
            breaking_news_page.properties["wikidata"]
        )
        self.assertTrue(is_breaking_news)
        many_edits_not_breaking_news_page = Individual.objects.get(identity="Q626900")
        is_not_breaking_news = WikipediaRankProcessor.breaking_news(
            many_edits_not_breaking_news_page.properties,
            many_edits_not_breaking_news_page.properties["wikidata"]
        )
        self.assertFalse(is_not_breaking_news)

    def test_number_of_deaths(self):
        lethal_event_page = Individual.objects.get(identity="Q42440670")
        number_of_deaths = WikipediaRankProcessor.number_of_deaths(
            lethal_event_page.properties,
            lethal_event_page.properties["wikidata"]
        )
        self.assertEqual(number_of_deaths, 8)
        no_event_page = Individual.objects.get(identity="Q626900")
        number_of_deaths = WikipediaRankProcessor.number_of_deaths(
            no_event_page.properties,
            no_event_page.properties["wikidata"]
        )
        self.assertEqual(number_of_deaths, 0)
