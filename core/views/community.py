from .base import DataScopeView


class CommunityView(DataScopeView):
    """
    TODO: allow actions who's function lives on a Community

    Return structure:
    {
        "actions": ["fetch_more_images"],
        "status": { },
        "result: { },
        "results": []
    }
    """

    @staticmethod
    def get_community_from_request(request):
        """

        :param request:
        :return: a Community ContentModel
        """
        pass


class PlainCommunityView(CommunityView):
    pass