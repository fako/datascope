import json, pickle

from celery import group
from celery.result import AsyncResult, GroupResult

from HIF.models.storage import ProcessStorage
from HIF.exceptions import HIFCouldNotLoadFromStorage
from HIF.tasks import execute_process
from HIF.helpers.storage import get_process_from_storage


class Status(object):
    NONE = 0
    DONE = 1
    PROCESSING = -1
    WAITING = -2
    EXTERNAL_SERVER_ERROR = -3
    EXTERNAL_REQUEST_ERROR = -4


class Process(ProcessStorage):

    _data = None

    def __iter__(self):
        return iter(self.results)

    @property
    def data(self):
        return self._data

    # This is a function to extend
    # It starts the tasks necessary to do the processing
    # It should store the celery task_id into task
    def process(self):
        return []

    # This is a function to extend.
    # It should save and return the results based on task_id results
    def post_process(self):
        return self.data

    def execute(self, *args, **kwargs):
        # Update config with kwargs
        if kwargs:
            self.config(**kwargs)
        # Set arguments as identifier
        self.identifier = self.identity(*args)
        print "Executing with {}".format(self.identifier)
        self.args = args

        # gets retained processes from the db.
        try:
            self.load()
            print "Loaded from cache: {}".format(self.identifier)
        except HIFCouldNotLoadFromStorage:
            pass

        # Process according to state
        if self.data is None:
            print "Started processing"
            self.status = Status.PROCESSING
            self.results = []
            self._data = self.process()
            assert self._data is not None, "Improper usage: a Process.process() returned None"

        if self.data and not self.results: # processing done, store it
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

    @property
    def data(self):

        if self._data and self._data != self.task:
            print "early return in data"
            return self._data
        if self.task:
            async_result = AsyncResult(self.task)
            if async_result.ready():
                self._data = async_result.result
                if async_result.successful():
                    return self._data
                else:
                    raise self._data
            else:
                return None
        else:
            return None

    class Meta:
        proxy = True


class GroupProcess(AsyncProcess):

    HIF_private = ["_process","_argument_key","_result_key"]

    def process(self):
        # Construct keyword arguments collection
        print self.args
        print self.config.dict(private=True)
        processes = []
        for arg in self.args:
            process = self.config._process(self.config.dict(protected=True))
            if not isinstance(arg, list):
                arg = [arg]
            processes.append((arg,process.retain(),))

        print "inside group process"
        print processes

        # Start a task that calls class_process in multiple different ways
        grp = group(execute_process.s(input,process) for input, process in processes).delay()
        self.task = grp.id

        return self.task

    def post_process(self):
        data = self.data[1] # data should contain a tuple with format (task_id, data)
        print "group post_process"
        print(self.data)
        print(data)
        self.results = []
        for arg, task_id in zip(self.args, data):
            rsl = AsyncResult(task_id).result
            prc = get_process_from_storage(rsl)
            self.results.append({
                self.config._argument_key: arg,
                self.config._result_key: prc.result
            })
        return self.results

    class Meta:
        proxy = True
