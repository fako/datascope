class DSHttpResourceException(Exception):

    def __init__(self, message, resource):
        super(DSHttpResourceException, self).__init__(message)
        self.resource = resource


class DSHttpError50X(DSHttpResourceException):
    pass


class DSHttpError40X(DSHttpResourceException):
    pass


class DSHttpWarning300(DSHttpResourceException):
    pass


class DSProcessException(Exception):
    pass


class DSProcessUnfinished(DSProcessException):
    pass


class DSProcessError(DSProcessException):
    pass