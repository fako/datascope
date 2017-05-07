from core.views.community import HtmlCommunityView


class SearchDumpCommunityView(HtmlCommunityView):

    @staticmethod
    def data_for(community_class, response=None):
        data = HtmlCommunityView.data_for(community_class, response)
        if data is None:
            data = {}
        data["topics"] = {
            "immigration"
        }
        return data
