# MODELS
class HIFDBResponse(Exception):
    pass


# INPUT
class HIFInputError(Exception):
    pass

class HIFHTTPError50X(HIFInputError):
    pass

class HIFHTTPError40X(HIFInputError):
    pass

class HIFDataLinkPending(HIFInputError):
    pass