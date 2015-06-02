class CommunityView(object):
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

    def get_config_from_request(self, request):
        """
        Gets a configuration dictionary from the user and GET params on request.

        :param request:
        :return:
        """
        pass


class PlainCommunityView(CommunityView):
    pass