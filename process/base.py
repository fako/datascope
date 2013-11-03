import json

from celery.result import AsyncResult

from HIF.models.storage import ProcessStorage
from HIF.exceptions import HIFCouldNotLoadFromStorage


class Status(object):
    NONE = 0
    DONE = 1
    PROCESSING = -1
    WAITING = -2
    EXTERNAL_SERVER_ERROR = -3
    EXTERNAL_REQUEST_ERROR = -4


class Process(ProcessStorage):

    _async = False

    # This functions indicates Celery's process
    def ready(self):
        if self.task:
            return AsyncResult(self.task).ready()
        else:
            return self.status == Status.DONE

    # This is a function to extend
    # It starts the tasks necessary to do the processing
    # It should store the celery task_id into task
    def process(self, *args, **kwargs):
        return False

    # This is a function to extend.
    # It should save and return the results based on task_id results
    def post_process(self, *args, **kwargs):
        return None

    def execute(self, *args, **kwargs):
        # Set arguments as identifier
        self.identifier = json.dumps(args) + ' | ' + json.dumps(kwargs)
        print "Executing with {}".format(self.identifier)
        self.args = args
        self.kwargs = kwargs

        # gets hibernating processes from the db.
        try:
            self.load()
            import ipdb; ipdb.set_trace()
            print "Loaded from cache: {}".format(self.identifier)
        except HIFCouldNotLoadFromStorage:
            pass

        # Process according to state
        if not self.ready() and self.status == Status.NONE:
            print "Started processing"
            self.status = Status.PROCESSING
            self.process()

        if self.ready() and not self.results: # processing done, store it
            print "Processing done, post processing"
            results = self.post_process()
            self.results = json.dumps(results)
            self.status = Status.DONE
            return results
        elif self.task: # Celery process busy
            print "Celery busy"
            return self.status == Status.PROCESSING
        else:
            print "Returning stored results"
            return self.results

    class Meta:
        proxy = True
