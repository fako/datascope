import logging
from itertools import zip_longest, starmap

from datagrowth.exceptions import DGNoContent

from core.models.resources.http import BrowserResource


log = logging.getLogger("datascope")


class GoogleTranslate(BrowserResource):

    URI_TEMPLATE = "https://translate.google.nl/#{}/{}/{}"

    def transform(self, soup):
        """

        :return:
        """
        confidences = soup.find_all(class_="gt-baf-cts")
        words = soup.find_all(class_="gt-baf-word-clickable")
        meanings = soup.find_all(class_="gt-baf-translations")

        def process_info(word, meaning, confidence):
            if word is None:
                raise DGNoContent("GoogleTranslate could not find any content for: {}".format(self.uri))
            word = word.text
            if meaning is not None:
                meaning = meaning.text
            if confidence is not None:
                confidence = int(confidence["style"].split(" ")[1][:-3])  # confidence expressed like: "width: 24px;"
            return word, meaning, confidence

        if not words:
            try:
                words = [
                    word for word in soup.find_all(class_="tlid-translation")
                ]
            except StopIteration:
                log.error("No fallback for: {}".format(self.uri))

        info = zip_longest(words, meanings, confidences)

        return [
            {
                "language": self.request["args"][1],
                "word": word,
                "meanings": meaning,
                "confidence": confidence
            }
            for word, meaning, confidence in starmap(process_info, info)
        ]
