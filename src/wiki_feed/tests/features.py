from django.test import TestCase

from core.models import Individual
from sources.processors.wikipedia.rank import WikipediaRankProcessor, users_watch, categories_watch, claim_watch


class TestWikiFeedFeatures(TestCase):

    fixtures = [
        "features"
    ]

    def test_many_concurrent_editors(self):
        many_concurrent_editors_page = Individual.objects.get(identity="Q42440670")
        is_breaking_news = WikipediaRankProcessor.many_concurrent_editors(
            many_concurrent_editors_page.properties,
            many_concurrent_editors_page.properties["wikidata"]
        )
        self.assertTrue(is_breaking_news)
        many_edits_not_concurrent_page = Individual.objects.get(identity="Q626900")
        is_not_breaking_news = WikipediaRankProcessor.many_concurrent_editors(
            many_edits_not_concurrent_page.properties,
            many_edits_not_concurrent_page.properties["wikidata"]
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


class TestWikiFeedFeaturesHelpers(TestCase):

    fixtures = [
        "features"
    ]

    def test_users_watch(self):
        page = Individual.objects.get(identity="Q42440670")
        number_of_users = users_watch([
            "Pharaoh of the Wizards",
            "Another Believer",
            "FallingGravity",
            "100.12.206.41",
            "2606:6000:FF81:4100:7C04:E13B:1EFA:2440",
            "Fako85",
            "0.0.0.0"
        ], page_data=page.properties)
        self.assertEqual(number_of_users, 5)

    def test_categories_watch(self):
        page = Individual.objects.get(identity="Q42440670")
        number_of_categories = categories_watch([
            "Category:Islamic terrorist incidents in 2017",
            "Category:Islamic terrorist incidents in 2016",
            "Category:Islamic terrorist incidents in 2015",
            "Category:Terrorist incidents in the United States in 2017",
            "Category:Terrorist incidents in the United States in 2016",
            "Category:Terrorist incidents in the United States in 2015"
        ], page_data=page.properties)
        self.assertEqual(number_of_categories, 2)

    def test_claim_watch(self):
        page = Individual.objects.get(identity="Q42440670")
        is_vehicle_ramming_attack = claim_watch("P31", "Q18711682", page.properties["wikidata"])
        self.assertTrue(is_vehicle_ramming_attack)
        is_childrens_party = claim_watch("P31", "Q5098265", page.properties["wikidata"])
        self.assertFalse(is_childrens_party)
        is_woman = claim_watch("P21", "Q6581097", page.properties["wikidata"])
        self.assertFalse(is_woman)
