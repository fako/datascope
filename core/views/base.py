class DataScopeView(object):
    """
    TODO: allow filtering based on GET parameters prefixed with $
    TODO: allow partial responses by respecting json paths after # in the URL

    TODO: allow GET, POST (action), PUT, DELETE
    """
    def get_config_from_request(self, request):
        """
        Gets a configuration dictionary from the user and GET params on request.

        :param request:
        :return:
        """
        pass