import integration  # do not import TestCase classes directly, or they will get tested!

from django.test import TestCase

from HIF.input.http.wiki import WikiTranslate


# class TestWikiLink(TestCase):
#
#     def setUp(self):
#         self.instance = GoogleLink()
#         self.instance.setup()


class TestWikiTranslate(integration.TestExternalResourceIntegration):

    HIF_model = WikiTranslate

    def test_wiki_translate_prepare_link(self):
        self.instance.setup(source_language='en', translate_to='nl')
        link = self.instance.prepare_link()
        self.assertIn("en.wik", link)

    def test_wiki_translate_prepare_params(self):
        self.instance.setup(source_language='en', translate_to='nl')
        params = self.instance.prepare_params()
        self.assertIn("iwprefix=nl", params)
