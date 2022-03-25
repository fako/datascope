import logging
from itertools import zip_longest, starmap
import json

from datagrowth.exceptions import DGNoContent
from datagrowth.resources import ShellResource

from core.models.resources.http import BrowserResource


log = logging.getLogger("datascope")


class GoogleTranslate(BrowserResource):

    URI_TEMPLATE = "https://translate.google.nl/#{}/{}/{}"

    def transform(self, soup):
        """

        :return:
        """
        confidences = soup.find_all(class_="gt-baf-entry-score")
        words = soup.find_all(class_="gt-baf-word-clickable")
        meanings = soup.find_all(class_="gt-baf-translations")

        def process_info(word, meaning, confidence):
            if word is None:
                raise DGNoContent("GoogleTranslate could not find any content for: {}".format(self.uri))
            word = word.text
            if meaning is not None:
                meaning = meaning.text
            if confidence is not None:
                confidence = len(confidence.find_all(class_="filled"))  # confidence expressed with filled and empty div
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


class GoogleTranslateShell(ShellResource):

    CMD_TEMPLATE = ["trans", "-dump", "--source={}", "--target={}", "{}"]

    def handle_errors(self):
        if "Please try your request again later." in self.stdout:
            self.status = 1
            self.stderr = "Please try your request again later."
            self.save()
        super().handle_errors()

    @property
    def content(self):
        content_type, plain_data = super().content
        if not plain_data:
            return content_type, plain_data

        # Validate and extract the data we need
        split_data = plain_data.split("\r\n")
        if not isinstance(split_data, list):
            raise DGNoContent("Translation failed to provide API data")
        api_data = json.loads(split_data[1])
        if not isinstance(api_data, list) or len(api_data) < 2:
            raise DGNoContent("Translation provided unexpected API data")
        translate_data = api_data[1]
        if translate_data is None:
            # Dealing with limited translation data we'll do the most we can
            word_data = api_data[0][0]
            return "application/json", [{
                "language": self.command["args"][1],
                "word": word_data[0],
                "meanings": [word_data[1]],
                "confidence": None
            }]
        noun_data = next((data for data in translate_data if data[0] == "noun"), None)
        if not isinstance(noun_data, list) or len(noun_data) < 3:
            raise DGNoContent("Translation provided unexpected translate data")

        return "application/json", [
            {
                "language": self.command["args"][1],
                "word": word_data[0],
                "meanings": word_data[1],
                "confidence": word_data[3] if len(word_data) >= 4 else None
            }
            for word_data in noun_data[2]
        ]
