from datagrowth.exceptions import DGResourceException as DSResourceException
from datagrowth.exceptions import (DGShellError as DSShellError, DGHttpError50X as DSHttpError50X,
                                   DGHttpError40X as DSHttpError40X)


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
