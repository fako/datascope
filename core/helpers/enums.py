class ProcessStatus(object):

    UNPROCESSED = 0
    DONE = 1

    PROCESSING = 2
    WAITING = 3
    READY = 4

    ERROR = -1
    WARNING = -2
    CANCELLED = -3


class ServiceTemplate(object):

    INDEX = "index.html"
    ACCEPTED = "accepted.html"
    OK = "ok.html"
    NO_CONTENT = "no-content.html"
    BAD_REQUEST = "bad-request.html"