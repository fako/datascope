from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from wiki_news.models import WikiNewsCommunity


class TestWikiNewsCommunity(TestCase):

    def setUp(self):
        super(TestWikiNewsCommunity, self).setUp()
        self.instance = WikiNewsCommunity()
        self.instance.save()

    def test_setup_growth(self):
        self.instance.setup_growth()
        self.assertEqual(self.instance.growth_set.count(), 2)

    def test_next_growth(self):
        self.instance.setup_growth()
        growth = self.instance.next_growth()
        self.assertEqual(growth.type, "revisions")