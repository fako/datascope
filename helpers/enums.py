class ProcessStatus(object):
    NONE = 0
    DONE = 1
    PROCESSING = -1
    WAITING = -2
    EXTERNAL_SERVER_ERROR = -3
    EXTERNAL_REQUEST_ERROR = -4