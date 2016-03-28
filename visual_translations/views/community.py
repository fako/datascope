from itertools import groupby

from core.views.community import HtmlCommunityView


class VisualTranslationsHtmlView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response):
        data = HtmlCommunityView.data_for(community_class, response)
        if response.status_code == 200:
            locale_key = lambda obj: obj["locale"]
            data["results"].sort(key=locale_key)
            response.data["results"] = [(lang, list(words),) for lang, words in groupby(data["results"], locale_key)]
            return response.data
        else:
            return response.data
