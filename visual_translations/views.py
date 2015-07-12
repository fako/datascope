from itertools import groupby

from core.views.community import HtmlCommunityView


class VisualTranslationsHtmlView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response):
        data = HtmlCommunityView.data_for(community_class, response)
        if response.status_code == 200:
            lang_key = lambda obj: obj["language"]
            data["results"].sort(key=lang_key)
            response.data["results"] = [(lang, list(words),) for lang, words in groupby(data["results"], lang_key)]
            return response.data
        else:
            return response.data