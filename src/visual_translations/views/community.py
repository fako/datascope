from itertools import groupby

from core.views.community import HtmlCommunityView


class VisualTranslationsHtmlView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response):
        data = HtmlCommunityView.data_for(community_class, response)
        if response.status_code == 200:
            locale_key = lambda obj: obj["language"] + "_" + obj["country"]
            data["results"].sort(key=locale_key)
            response.data["results"] = [(lang, list(words),) for lang, words in groupby(data["results"], locale_key)]
            return response.data
        else:
            return response.data

    @staticmethod
    def html_template_for(community_class, response):
        """
        All variants share the same HTML render.
        So we modify the template to be named the same across variants.
        """
        template = HtmlCommunityView.html_template_for(community_class, response)
        return template.replace(community_class.get_name(), "visual_translations")


class VisualTanslationsDisambiguationView(VisualTranslationsHtmlView):

    @staticmethod
    def html_template_for(community_class, response):
        return "visual_translations/disambiguation.html"
