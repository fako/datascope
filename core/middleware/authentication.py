from core.models.user import DataScopeUser, DataScopeAnonymousUser


class DataScopeUserMiddleware(object):

    @staticmethod
    def process_request(request):
        if hasattr(request, 'user') and request.user.is_authenticated():
            request.user.__class__ = DataScopeUser
        if hasattr(request, 'user') and request.user.is_anonymous():
            request.user.__class__ = DataScopeAnonymousUser