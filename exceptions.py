# Storage
class HIFCouldNotLoadFromStorage(Exception):
    pass

# INPUT
class HIFInputError(Exception):
    pass

class HIFHttpError50X(HIFInputError):
    pass

class HIFHttpError40X(HIFInputError):
    pass

class HIFHttpLinkPending(HIFInputError):
    pass

class HIFEndOfInput(Exception):
    pass