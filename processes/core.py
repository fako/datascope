import traceback

import requests

from django.db.models.loading import get_model

from celery import group
from celery.result import AsyncResult, GroupResult

from HIF.models.storage import ProcessStorage
from HIF.exceptions import HIFProcessingError, HIFProcessingAsync, \
    HIFEndlessLoop, HIFEndOfInput, HIFInputError, HIFImproperUsage
from HIF.tasks import execute_process
from HIF.helpers.enums import ProcessStatus as Status




class Process(ProcessStorage):

    HIF_child_process = ''

    def __iter__(self):
        return iter(self.rsl)


    def process(self):
        """
        This is a function to extend
        It starts the tasks necessary to do the processing
        It should store a celery task in tsk or store results in rsl
        """
        pass


    def post_process(self):
        """
        This is a function to extend.
        It should store results using content on prcs or txts
        """
        pass

    def extract_task(self):
        ser_prc = self.task.result
        self.subs.add(ser_prc)



    @property
    def rsl(self):
        if self.status == Status.DONE:
            return self.results
        elif self.status in [Status.ERROR, Status.WARNING]:
            raise HIFProcessingError()
        elif self.status in [Status.PROCESSING, Status.WAITING, Status.READY]:
            raise HIFProcessingAsync()
    @rsl.setter
    def rsl(self, results):
        self.results = results
        self.status = Status.DONE


    @property
    def task(self):
        if not self.task_id:
            raise ValueError("Process does not have a task set")
        else:
            return AsyncResult(self.task_id)
    @task.setter
    def task(self, task):
        self.task_id = task.id
        self.status = Status.PROCESSING


    # TODO: subs does not split between texts and processes status. should it?
    def subs_errors(self):
        return self.subs.count({"status__in":[Status.ERROR, Status.WARNING]})

    def subs_waiting(self):
        x = self.subs.count({"status__in":[Status.PROCESSING, Status.WAITING, Status.READY]})
        print x
        return x

    def subs_state(self):
        # Wakeup child processes if they are there
        if self.status == Status.WAITING and self.HIF_child_process:
            self.subs.run(self.HIF_child_process, 'execute')
        # Recheck the state of subcontent
        if self.subs_waiting() != 0:
            self.status = Status.WAITING
        elif self.subs_waiting() == 0:
            self.status = Status.READY
        # If there are errors in child processes we go into warning mode
        if self.subs_errors() != 0:
            self.status = Status.WARNING


    def execute(self, *args, **kwargs):
        """
        ..............
        """

        self.setup(*args, **kwargs)

        # START
        if self.status == Status.UNPROCESSED:
            try:
                self.retain()
                self.process()
            except Exception as exception:
                self.exception = exception
                self.traceback = traceback.format_exc()
                self.status = Status.ERROR

        # ASYNC PROCESSING
        if self.status == Status.PROCESSING:
            if self.task.successful():
                # Fetch results from Celery
                self.extract_task()
                # Set state based on async results in substorage
                self.subs_state()

            # In rare cases the task itself raised an exception
            # Process goes into error mode
            if self.task.failed():
                self.exception = self.task.result
                self.status = Status.ERROR

        # WAITING
        if self.status == Status.WAITING:
            # Reset state based on content of substorage
            # GroupProcess will execute all its subprocesses
            self.subs_state()

        # READY
        if self.status == Status.READY:
            # All content in substorage is done
            try:
                self.post_process()
                self.retain()
            except Exception as exception:
                self.exception = exception
                self.traceback = traceback.format_exc()
                self.status = Status.ERROR

        self.retain()

    class Meta:
        proxy = True



class Retrieve(Process):

    links = []


    def extract_continue_url(self, link):
        return ''


    def handle_exception(self, exception):
        for link in self.links:
            self.subs.add(link.retain())
        raise exception


    def continue_link(self, link):

        continue_url = self.extract_continue_url(link)
        if continue_url:
            pass # TODO: implement properly and write tests
            #continuation = self.config.class_link(config=self.kwargs)
            #continuation.identifier = continue_url
            #continuation.auth_link = continue_url
            #continuation.setup = False
            #return continuation
        else:
            raise HIFEndOfInput


    def process(self):

        # Make sure there is at least one argument to loop over
        if not self.args:
            args = self.args + ['']
        else:
            args = self.args

        link_model = get_model(app_label="HIF", model_name=self.config._link)
        if link_model is None:
            raise HIFImproperUsage("The specified link model does not exist or is not registered as Django model with HIF label.")

        session = requests.Session()

        results = []
        for arg in args:

            # Fetch link with continue links
            self.links = []
            link = link_model()
            link.session = session
            try:
                for repetition in range(100):
                    link.get(arg, **self.config.dict())
                    self.links.append(link)
                    link = self.continue_link(link)
                else:
                    raise HIFEndlessLoop("HIF stopped retrieving links after fetching 100 links. Does extract_continuation_url ever return an empty string?")
            except HIFInputError as exception:
                self.handle_exception(exception)
            except HIFEndOfInput:
                pass

            # Everything retrieved. We store it in results
            rsl = []
            for link in self.links:
                if self.config.debug:
                    self.subs.add(link.retain())
                for obj in link.data:
                    rsl.append(obj)
            results.append({
                "query": arg,  # may be empty when not dealing with QueryLinks
                "results": rsl
            })

        # After all arguments are fetched, we store everything in self.rsl and process becomes DONE
        self.rsl = results

    class Meta:
        app_label = "HIF"
        proxy = True




class GroupProcess(Process):

    HIF_private = ["_process"]

    @property
    def task(self):
        if not self.task_id:
            raise ValueError("Process does not have a task set")
        else:
            return GroupResult.restore(self.task_id)
    @task.setter
    def task(self, task):
        task.save()
        self.task_id = task.id
        self.status = Status.PROCESSING


    @property
    def data(self):
        return [prc.results for prc in self.subs[self.config._process]]

        ## Early return when we already formatted the data
        #if self.formatted:
        #    return self._data
        ## Get data as if it was coming from a normal process
        #self._data = super(GroupProcess, self).data
        #self.formatted = False
        ## Format GroupResult into list of results
        #if self._data:
        #    data = []
        #
        #    self._data = data
        #    self.formatted = True
        #return self._data

    def extract_task(self):
        # Every result in a group should return a Process
        # This single process could be a grouped process in turn
        for ar in self.task.results:
            ser_prc = ar.result
            self.subs.add(ser_prc)


    def process(self):
        # Construct keyword arguments collection
        process_model = get_model(app_label="HIF", model_name=self.config._process)

        processes = []
        for arg in self.args:
            process = process_model()
            process.setup(arg, **self.config.dict(protected=True))
            processes.append((arg,process.retain(),))

        # Start a task that calls class_process in multiple different ways
        grp = group(execute_process.s(inp, ser_prc) for inp, ser_prc in processes).delay()
        self.task = grp


    #def post_process(self):
    #    data = self.data # data should contain list with process retain tuples
    #    print "group post_process"
    #    print(data)
    #
    #    results = []
    #    for arg, prc in zip(self.args, data):
    #        process = get_process_from_storage(prc)
    #        if process.status == Status.DONE:
    #            print arg, process.results
    #            results.append({
    #                self.config._argument_key: arg,
    #                self.config._result_key: process.results
    #            })
    #        else:
    #            return None
    #
    #    self.results = results
    #    return self.results

    class Meta:
        proxy = True
