class DGResourceException(Exception):

    def __init__(self, message, resource):
        super().__init__(message)
        self.resource = resource


class DGShellError(DGResourceException):
    pass


class DGHttpError50X(DGResourceException):
    pass


class DGHttpError40X(DGResourceException):
    pass
