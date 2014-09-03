import traceback
import requests
from copy import deepcopy

from django.db.models.loading import get_model

from celery import group
from celery.result import AsyncResult, GroupResult

from HIF.models.storage import ProcessStorage
from HIF.exceptions import HIFProcessingError, HIFProcessingAsync, \
    HIFEndlessLoop, HIFEndOfInput, HIFInputError, HIFImproperUsage, HIFNoContent
from HIF.tasks import execute_process
from HIF.helpers.enums import ProcessStatus as Status
from HIF.helpers.mixins import DataMixin
from HIF.helpers.data import reach
from HIF.helpers.storage import get_hif_model


class Process(ProcessStorage):

    HIF_child_process = ''

    HIF_extension_statusses = [200]  # TODO: sane default

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
            if self.results:
                return self.results
            else:
                raise HIFNoContent()
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


    def extend(self, ser_extendee):
        """
        This method looks at extend configuration and adjusts arguments and configuration of process based on that.


        This method adds an entry called extending to the meta field
        That entry specifies how the results should be merged by extendee
        meta = {
            "extending": OriginalDict
        }
        It also sets extends field for database filtering

        Should check statusses are in correct range

        This method returns raises exceptions if extendee can't be worked with
        """
        Extendee = get_hif_model(ser_extendee)
        extendee = Extendee().load(serialization=ser_extendee)  # TODO: write test that makes sure this function does not change extendee

        # TODO: make status checks possible by registering later
        #if extendee.status not in self.HIF_extension_statusses:
        #    self.status = Status.CANCELLED
        #    raise Exception('status is wrong!')

        if 'keypath' not in self.config._extend:
            self.status = Status.ERROR
            raise HIFImproperUsage('Keypath is not present in extend config during extending')

        self.extends = self.__class__.__name__  # TODO: check that this works

        source = reach(self.config._extend['keypath'], extendee.rsl)
        self.meta = {'extending': source}

        # Pad self.arguments with args from extend config
        if 'args' in self.config._extend:
            args = self.arguments or []
            for keypath in self.config._extend['args']:
                arg = reach(keypath, source)
                if arg not in args:
                    args.append(arg)
            self.arguments = args

        # Pad config with extend kwargs
        if 'kwargs' in self.config._extend:
            kwargs = {}
            for kw, keypath in self.config._extend['kwargs'].iteritems():
                kwargs[kw] = reach(keypath, source)
            self.config(kwargs)




    @property
    def extension(self):
        """
        Returns the keypath that is supposed to be replaced and the extended object
        """
        extension = self.meta['extending']
        extension[self.config._extend["extension"]] = self.rsl
        return self.config._extend["keypath"], extension

    # TODO: subs does not split between texts and processes status. should it?
    # TODO: subs should work with ManyToMany not with dictionary
    def subs_errors(self):
        return self.subs.count({"status__in":[Status.ERROR, Status.WARNING]})

    def subs_waiting(self):
        return self.subs.count({"status__in":[Status.PROCESSING, Status.WAITING, Status.READY]})

    def subs_update(self):
        # Wakeup child processes if they are there
        if self.status == Status.WAITING and self.HIF_child_process:  # TODO: this locks a process to one other process
            self.subs.run(self.HIF_child_process, 'execute')
        # Recheck the state of subcontent
        if self.subs_waiting() != 0:
            self.status = Status.WAITING
        elif self.subs_waiting() == 0:
            self.status = Status.READY
        # If there are errors in child processes we go into warning mode
        if self.subs_errors() != 0:
            self.status = Status.WARNING

    def subs_extend(self):
        """
        Should filter for all subs with an extends field set to this class

        """
        pass


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
                self.subs_update()

            # In rare cases the task itself raised an exception
            # Process goes into error mode
            if self.task.failed():
                self.exception = self.task.result  # TODO: fix for groups
                self.status = Status.ERROR

        # WAITING
        if self.status == Status.WAITING:
            # Reset state based on content of substorage
            # GroupProcess will execute all its subprocesses
            self.subs_update()

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

    def handle_exception(self, exception):
        for link in self.links:
            self.subs.add(link.retain())
        raise exception

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

        for arg in args:  # TODO: this still allows for Falsy values, check also QueryLink

            # Fetch link with continue links
            self.links = []
            link = link_model()
            link.session = session
            try:
                for repetition in range(100):
                    # TODO: what is necessary
                    self.config(link.next_params)
                    link.get(arg, **self.config.dict())  # TODO: problems with calling setup too often here
                    link.retain()  # TODO: will need some testing to assure quality
                    old = deepcopy(link)
                    self.links.append(old)
                    link.pk = None
                    link.prepare_next()
                else:
                    raise HIFEndlessLoop("HIF stopped retrieving links after fetching 100 links. Does extract_continue_url ever return an empty string?")
            except HIFInputError as exception:
                self.handle_exception(exception)
            except HIFEndOfInput:
                pass

            # Everything retrieved. We store it in results
            # link.rsl will yield either response body or the data
            # specify link.rsl behavior (and what results will be) in the link class
            if len(self.links) == 0:
                results = None
            elif len(self.links) == 1:
                link = self.links[0]
                if self.config.debug:
                    self.subs.add(link.retain())
                results = link.rsl
            else:
                results = []
                for link in self.links:
                    if self.config.debug:
                        self.subs.add(link.retain())
                    if isinstance(link.rsl, dict):
                        results.append(link.rsl)
                    else:  # presuming list
                        results + link.rsl

        # After all arguments are fetched, we store everything in self.rsl and process becomes DONE
        self.rsl = results

    class Meta:
        app_label = "HIF"
        proxy = True




class GroupProcess(Process, DataMixin):

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
    def data_source(self):
        # TODO: the way we retrieve the original arguments here seems naive.
        results = [(prc.arguments[0], prc.results,) for prc in self.subs[self.config._process]]
        source = [{"member": arg, "data": rsl} for arg, rsl in results if rsl]
        return source

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
            processes.append((arg, process.retain(),))

        # Start a task that calls class_process in multiple different ways
        grp = group(execute_process.s(inp, ser_prc) for inp, ser_prc in processes).delay()
        self.task = grp


    class Meta:
        proxy = True
