class DSResourceException(Exception):

    def __init__(self, message, resource):
        super(DSResourceException, self).__init__(message)
        self.resource = resource


class DSHttpError50X(DSResourceException):
    pass


class DSHttpError40X(DSResourceException):
    pass


class DSHttpError403LimitExceeded(DSResourceException):
    pass


class DSHttpError400NoToken(DSResourceException):
    pass


class DSHttpWarning300(DSResourceException):
    pass


class DSHttpWarning204(DSResourceException):
    pass


class DSInvalidResource(DSResourceException):
    pass


class DSNoContent(Exception):
    pass


class DSProcessException(Exception):
    pass


class DSProcessUnfinished(DSProcessException):
    pass


class DSProcessError(DSProcessException):
    pass


class DSSystemConfigError(Exception):
    pass


class DSFileLoadError(Exception):
    pass
