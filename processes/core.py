import traceback, json

from django.db.models.loading import get_model

from celery import group
from celery.result import AsyncResult

from HIF.models.storage import ProcessStorage
from HIF.exceptions import HIFProcessingError, HIFProcessingAsync, \
    HIFEndlessLoop, HIFEndOfInput, HIFInputError, HIFImproperUsage
from HIF.tasks import execute_process
from HIF.helpers.enums import ProcessStatus as Status




class Process(ProcessStorage):


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


    #def subscribe(self, to):
    #    if to not in self.subs:
    #        self.subs.append(to)
    #        self.retain()
    #
    #
    #def inform(self):
    #    for tprc in self.subs:
    #        cls, prc_id = tprc
    #        prc = cls()
    #        prc.load(prc_id)
    #        prc.execute()
    #    self.subs = []


    @property
    def rsl(self):
        if self.status == Status.DONE:
            return self.results
        elif self.status in [Status.ERROR, Status.WARNING]:
            raise HIFProcessingError()
        elif self.status in [Status.WAITING, Status.SUBSCRIBED, Status.READY]:
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
    def task(self, task_id):
        self.task_id = task_id
        self.status = Status.WAITING


    # TODO: subs does not split between texts and processes status. should it?
    def subs_errors(self):
        return self.subs.count({"status__in":[Status.ERROR, Status.WARNING]})

    def subs_waiting(self):
        return self.subs.count({"status__in":[Status.WAITING, Status.SUBSCRIBED, Status.READY]})


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
        if self.status == Status.WAITING:
            ar = self.task
            if ar.successful():

                # This part assumes that AsyncResults contains at least one Process
                # A HIF task at the end of a chain should never return results directly,
                # but always the Process(es) responsible
                if ar.result[0] != self.task_id:
                    # We are dealing with a singleton
                    ser_prc = ar.result
                    self.subs.add(ser_prc)
                else:
                    # We are dealing with a group
                    # Every result in a group should return a Process
                    # This single process could be a grouped process in turn
                    for task_id, trash in ar.result[1]: # second element of data contains array with task_ids
                        ser_prc = AsyncResult(task_id).result
                        self.subs.add(ser_prc)

                # When there are waiting Processes we subscribe self to everything based on last added tprc
                if self.subs_waiting() != 0:
                    #type, prc_id, obj_id = tprc
                    #prc = ContentType.objects.get_for_id(self, prc_id).get_objects_for_this_type(id=obj_id)
                    #self.prcs.subscribe(prc, self.serialize())  # TODO: needs a retain tuple probably
                    self.status = Status.SUBSCRIBED
                elif self.subs_waiting() == 0:
                    self.status = Status.READY
                # If there are errors in child processes we go into warning mode
                if self.subs_errors() != 0:
                    self.status = Status.WARNING

            # In rare cases the task itself raised an exception
            # Process goes into error mode
            elif ar.failed():
                self.exception = ar.result
                self.status = Status.ERROR

        # SUBSCRIBED
        if self.status == Status.SUBSCRIBED:
            if self.subs_errors () != 0:
                self.status = Status.WARNING
            if self.subs_waiting() == 0:
                self.status = Status.READY

        # READY
        if self.status == Status.READY:
            try:
                self.post_process()
                self.retain()
                #self.inform()
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
            raise HIFImproperUsage("The specified link model does not exist or is not registered as Django model.")

        results = []
        for arg in args:

            # Fetch link with continue links
            self.links = []
            link = link_model()
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




#class GroupProcess(Process):
#
#    HIF_private = ["_process","_argument_key","_result_key"]
#
#    @property
#    def data(self):
#        # Early return when we already formatted the data
#        if self.formatted:
#            return self._data
#        # Get data as if it was coming from a normal process
#        self._data = super(GroupProcess, self).data
#        self.formatted = False
#        # Format GroupResult into list of results
#        if self._data:
#            data = []
#
#            self._data = data
#            self.formatted = True
#        return self._data
#
#    def process(self):
#        # Construct keyword arguments collection
#        print self.args
#        print self.config.dict(private=True)
#        processes = []
#        for arg in self.args:
#            process = self.config._process(self.config.dict(protected=True))
#            processes.append((arg,process.retain(),))
#
#        print "inside group process"
#        print processes
#
#        # Start a task that calls class_process in multiple different ways
#        grp = group(execute_process.s(input,process) for input, process in processes).delay()
#        self.task = grp.id
#
#        return self.task
#
#    def post_process(self):
#        data = self.data # data should contain list with process retain tuples
#        print "group post_process"
#        print(data)
#
#        results = []
#        for arg, prc in zip(self.args, data):
#            process = get_process_from_storage(prc)
#            if process.status == Status.DONE:
#                print arg, process.results
#                results.append({
#                    self.config._argument_key: arg,
#                    self.config._result_key: process.results
#                })
#            else:
#                return None
#
#        self.results = results
#        return self.results
#
#    class Meta:
#        proxy = True
