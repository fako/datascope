from datagrowth.exceptions import DGResourceException as DSResourceException


class DSHttpError400NoToken(DSResourceException):
    pass


class DSHttpWarning300(DSResourceException):
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
