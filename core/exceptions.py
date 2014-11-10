from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_300_MULTIPLE_CHOICES


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

class HIFHttpWarning300(HIFInputError):
    def __init__(self, detail):
        self.status_code = HTTP_300_MULTIPLE_CHOICES
        self.detail = detail

class HIFHttpLinkPending(HIFInputError):
    pass

class HIFEndOfInput(Exception):
    pass

class HIFUnexpectedInput(HIFInputError):
    pass


# PROCESS
class HIFEndlessLoop(Exception):
    pass

class HIFProcessingError(Exception):
    pass

class HIFProcessingAsync(Exception):
    pass

class HIFProcessingWarning(Exception):
    pass

class HIFNoInput(Exception):
    pass

class HIFBadRequest(APIException):
    def __init__(self, detail):
        self.status_code = HTTP_400_BAD_REQUEST
        self.detail = detail