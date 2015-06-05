class DSResourceException(Exception):

    def __init__(self, message, resource):
        super(DSResourceException, self).__init__(message)
        self.resource = resource


class DSHttpError50X(DSResourceException):
    pass


class DSHttpError40X(DSResourceException):
    pass


class DSHttpWarning300(DSResourceException):
    pass


class DSInvalidResource(DSResourceException):
    pass


class DSProcessException(Exception):
    pass


class DSProcessUnfinished(DSProcessException):
    pass


class DSProcessError(DSProcessException):
    pass