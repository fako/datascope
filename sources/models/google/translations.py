from __future__ import unicode_literals, absolute_import, print_function, division

from core.models.resources.http import BrowserResource


class GoogleTranslate(BrowserResource):

    URI_TEMPLATE = "https://translate.google.nl/#{}/{}/{}"

    def transform(self, soup):
        """

        :return:
        """
        confidences = soup.find_all(class_="gt-baf-cts")
        words = soup.find_all(class_="gt-baf-word-clickable")
        meanings = soup.find_all(class_="gt-baf-translations")
        return [
            {
                "word": word.text,
                "meanings": meaning.text,
                "confidence": int(confidence["style"].split(" ")[1][:-3])  # confidence expressed like: "width: 24px;"
            }
            for confidence, word, meaning in zip(confidences, words, meanings)
        ]
