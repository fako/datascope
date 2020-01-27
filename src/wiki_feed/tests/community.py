from django.test import TestCase

from wiki_feed.models import WikiFeedCommunity


class TestWikiFeedCommunity(TestCase):

    def setUp(self):
        super(TestWikiFeedCommunity, self).setUp()
        self.instance = WikiFeedCommunity()
        self.instance.save()

    def test_setup_growth(self):
        self.instance.setup_growth()
        self.assertEqual(self.instance.growth_set.count(), 3)

    def test_next_growth(self):
        self.instance.setup_growth()
        growth = self.instance.next_growth()
        self.assertEqual(growth.type, "revisions")
