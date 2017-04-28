from core.models.resources.http import HttpResource


class KledingListing(HttpResource):

    URI_TEMPLATE = "https://www.kleding.nl{}"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }

    def next_parameters(self):
        mime_type, soup = self.content
        next_tag = soup.find(attrs={"rel":"next"})
        if not next_tag:
            return {}
        next_link = next_tag["href"]
        next_page = next_link[next_link.rfind("=") + 1:]
        return {
            "p": next_page
        }
