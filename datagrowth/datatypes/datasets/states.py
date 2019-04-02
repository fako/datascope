class DatasetState(object):
    NEW = "New"
    ASYNC = "Asynchronous"
    SYNC = "Synchronous"
    READY = "Ready"
    ABORTED = "Aborted"
    RETRY = "Retry"


DATASET_STATE_CHOICES = [
    (value, value) for attr, value in sorted(DatasetState.__dict__.items()) if not attr.startswith("_")
]
