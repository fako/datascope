class DSHttpResourceError(Exception):
    pass


class DSHttpError50X(DSHttpResourceError):
    pass


class DSHttpError40X(DSHttpResourceError):
    pass


class DSHttpWarning300(DSHttpResourceError):
    pass