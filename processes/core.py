import json

from celery import group
from celery.result import AsyncResult, GroupResult

from HIF.models.storage import ProcessStorage
from HIF.exceptions import HIFCouldNotLoadFromStorage
from HIF.tasks import execute_process


class Status(object):
    NONE = 0
    DONE = 1
    PROCESSING = -1
    WAITING = -2
    EXTERNAL_SERVER_ERROR = -3
    EXTERNAL_REQUEST_ERROR = -4


class Process(ProcessStorage):

    # This functions indicates Celery's process
    def ready(self):
        return self.status == Status.DONE

    # This is a function to extend
    # It starts the tasks necessary to do the processing
    # It should store the celery task_id into task
    def process(self):
        return False

    # This is a function to extend.
    # It should save and return the results based on task_id results
    def post_process(self):
        return None

    def execute(self, *args, **kwargs):
        # Update config with kwargs
        if kwargs:
            self.config(**kwargs)
        # Set arguments as identifier
        self.identifier = self.identity(*args)
        print "Executing with {}".format(self.identifier)
        self.args = args

        # gets hibernating processes from the db.
        try:
            self.load()
            print "Loaded from cache: {}".format(self.identifier)
        except HIFCouldNotLoadFromStorage:
            pass

        # Process according to state
        if not self.ready() and self.status == Status.NONE:
            print "Started processing"
            self.status = Status.PROCESSING
            self.results = []
            self.process()

        if self.ready() and not self.results: # processing done, store it
            print "Processing done, post processing"
            self.results = self.post_process()
            self.status = Status.DONE
            return self.results
        else:
            print "Returning cached or initial results"
            return self.results

    class Meta:
        proxy = True


class AsyncProcess(Process):

    def ready(self):
        if self.task:
            return AsyncResult(self.task).ready()
        else:
            return super(AsyncProcess,self).ready()

    class Meta:
        proxy = True


class GroupProcess(AsyncProcess):

    _config = ["class_process","vary_key","result_key"]
    _group_task = execute_process

    def ready(self):
        if self.task:
            return GroupResult(self.task).ready()
        else:
            return super(GroupProcess,self).ready()

    def process(self):
        # Create precedences
        self.save()

        # Construct keyword arguments collection
        ka_collection = []
        for arg in self.args:
            ka = dict(self.kwargs)
            ka[self.config.vary_key] = arg
            ka_collection.append(ka)

        # Start a task that calls class_process in multiple different ways
        grp = group(execute_process.s((self.config.class_process, self.id,), **ka) for ka in ka_collection).delay()
        self.task = grp.task_id # ???

        return True

    def post_process(self):
        self.results = []
        for vary_value, result in zip(self.kwargs[self.config.vary_key], GroupResult(self.task).collection()):
            rsl, trash = result
            self.results.append({
                self.config.vary_key: vary_value,
                self.config.result_key: rsl.result
            })
        return self.results

    class Meta:
        proxy = True
