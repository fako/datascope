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
