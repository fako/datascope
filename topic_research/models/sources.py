from core.models.resources.http import URLResource


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

            paragraph_group_texts = [paragraph_candidate.get_text()]
            processed_paragraphs.add(candidate_hash)
            for candidate_sibling in candidate_siblings:
                paragraph_group_texts.append(candidate_sibling.get_text())
                candidate_sibling_hash = hash(candidate_sibling)
                processed_paragraphs.add(candidate_sibling_hash)

            paragraph_groups.append(paragraph_group_texts)

        return paragraph_groups
