class CommunityState(object):
    NEW = "New"
    ASYNC = "Asynchronous"
    SYNC = "Synchronous"
    READY = "Ready"
    ABORTED = "Aborted"

COMMUNITY_STATE_CHOICES = [
    (value, value) for attr, value in sorted(CommunityState.__dict__.items()) if not attr.startswith("_")
    ]
