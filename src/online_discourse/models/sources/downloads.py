import os
import logging

from django.core.files.storage import default_storage
from django.db.models import signals

from datagrowth.resources import HttpFileResource, TikaResource, file_resource_delete_handler
from core.models.resources.http import URLResource


log = logging.getLogger("datascope")


class WebContentDownload(HttpFileResource):

    CONFIG_NAMESPACE = "discourse_download"

    @property
    def content(self):
        content_type, file = super().content
        if not file:
            return content_type, file
        variables = self.variables()
        return content_type, {
            self.config.url_key: variables["url"][0],
            self.config.resource_key: os.path.join(default_storage.location, self.body)
        }


signals.post_delete.connect(file_resource_delete_handler, sender=WebContentDownload)


class WebTextTikaResource(TikaResource):
    pass


class WebTextResource(URLResource):
    """
    A HttpResource made to get and extract web texts in a generic way
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    }

    @property
    def content(self):
        content_type, soup = super().content
        if content_type != "text/html":
            log.warning("Unsupported web text content type: {}".format(content_type))
            return None, None
        if soup:  # TODO: allow disabling this through config
            soup.paragraph_groups = self.extract_paragraph_groups(soup)
            soup.source = self.request["url"]
        return content_type, soup

    @staticmethod
    def extract_paragraph_groups(soup):
        paragraph_candidates = soup.find_all("p")
        processed_paragraphs = set()
        paragraph_groups = []

        for paragraph_candidate in paragraph_candidates:

            candidate_hash = hash(paragraph_candidate)
            if candidate_hash in processed_paragraphs:
                continue

            candidate_siblings = paragraph_candidate.find_next_siblings("p")
            if len(candidate_siblings) < 2:
                processed_paragraphs.add(candidate_hash)
                continue

            try:
                paragraph_group_texts = [paragraph_candidate.get_text()]
            except AttributeError:
                # html5lib bug: https://bugs.launchpad.net/beautifulsoup/+bug/1184417
                # switching to lxml not an option because it causes its own problems with broken (webby) pages
                # ignoring this p
                continue

            processed_paragraphs.add(candidate_hash)
            for candidate_sibling in candidate_siblings:
                paragraph_group_texts.append(candidate_sibling.get_text())
                candidate_sibling_hash = hash(candidate_sibling)
                processed_paragraphs.add(candidate_sibling_hash)

            paragraph_groups.append(paragraph_group_texts)

        return paragraph_groups
