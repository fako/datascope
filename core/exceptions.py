class DSHttpResourceError(Exception):

    def __init__(self, message, resource):
        super(DSHttpResourceError, self).__init__(message)
        self.resource = resource


class DSHttpError50X(DSHttpResourceError):
    pass


class DSHttpError40X(DSHttpResourceError):
    pass


class DSHttpWarning300(DSHttpResourceError):
    pass