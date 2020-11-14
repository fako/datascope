from urlobject import URLObject

from core.models.resources.http import HttpResource


def is_reddis_thing(element_id):
    return element_id and element_id.startswith('thing_')


class RedditList(HttpResource):

    URI_TEMPLATE = "https://www.reddit.com/r/{}/top/"

    PARAMETERS = {
        "sort": "top",
        "t": "all"
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    }

    def next_parameters(self):

        content_type, soup = self.content
        next_button = soup.find(class_="next-button")
        if next_button is None or not next_button.text:
            return {}

        current = URLObject(self.request.get("url"))

        position = int(current.query_dict.get("count", 0))
        things = soup.find_all(id=is_reddis_thing)
        last_thing = things[-1]
        return {
            "after": last_thing["id"][6:],  # takes the id minus "_thing"
            "count": position + 25
        }


class RedditPermalink(HttpResource):

    URI_TEMPLATE = "https://www.reddit.com{}"  # meant to include permalinks

    PARAMETERS = {
        "limit": 500
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
    }
