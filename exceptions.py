from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST


# General
class HIFImproperUsage(Exception):
    pass

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


# PROCESS
class HIFEndlessLoop(Exception):
    pass

class HIFProcessingError(Exception):
    pass

class HIFProcessingAsync(Exception):
    pass

class HIFNoInput(Exception):
    pass

class HIFNoContent(Exception):
    pass

class HIFBadRequest(APIException):
    def __init__(self, detail):
        self.status_code = HTTP_400_BAD_REQUEST
        self.detail = detail