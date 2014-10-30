import traceback
import requests
from copy import deepcopy

from celery import group
from celery.result import AsyncResult, GroupResult

from core.models.storage import ProcessStorage
from core.exceptions import (HIFProcessingError, HIFProcessingAsync, HIFInputError, HIFNoContent)
from core.tasks import execute_process
from core.helpers.enums import ProcessStatus as Status
from core.helpers.mixins import DataMixin
from core.helpers.storage import get_hif_model


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

    def extract_task(self):
        ser_prc = self.task.result
        self.rgs.add(ser_prc)


    @property
    def rsl(self):
        if self.status == Status.DONE:
            if self.results:
                return self.results
            else:
                raise HIFNoContent()
        elif self.status == Status.ERROR:
            raise HIFProcessingError()
        elif self.status == Status.WARNING:
            return self.results  # outside determines if results are valid.
        elif self.status in [Status.PROCESSING, Status.WAITING, Status.READY]:
            raise HIFProcessingAsync()
    @rsl.setter
    def rsl(self, results):
        self.results = results
        self.status = Status.DONE

    @property
    def reports(self):
        reports = self.rgs.reports()
        reports = list(reports) if reports is not None else []
        for rprts in self.rgs.attr('reports', cls=self.rgs._processes):
            if rprts is not None:
                reports += list(rprts)
        return reports


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
                self.meta = getattr(exception, 'report', None)
                self.status = Status.ERROR

        # ASYNC PROCESSING
        if self.status == Status.PROCESSING:
            if self.task.successful():
                # Fetch results from Celery
                self.extract_task()
                # Set state based on async results in substorage
                self.update_status()

            # In rare cases the task itself raised an exception
            # Process goes into error mode
            if self.task.failed():
                self.exception = self.task.result  # TODO: fix for groups
                self.status = Status.ERROR

        # WAITING
        if self.status == Status.WAITING:
            # Reset state based on content of substorage
            # GroupProcess will execute all its subprocesses
            self.update_status()

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

    def handle_exception(self, exception, error_link):
        # Save data from erroneous link
        self.rgs.add(error_link.retain())

        # Save links so far
        for link in self.links:
            self.rgs.add(link.retain())

        exception.report = {
            "type": error_link.type,
            "status": error_link.status,
            "message": str(exception),
            "url": error_link.url,
        }
        raise exception

    def process(self):
        """

        :return:
        """

        # Make sure there is at least one argument to loop over
        if not self.args:
            args = ['']
        else:
            args = self.args

        # Prepare some vars
        session = requests.Session()
        link_model = get_hif_model(self.config._link)
        link_context = self.config.dict()

        self.links = []

        for arg in args:

            link = link_model()
            link.session = session
            link_context.update(link.next_params)  # separates calls to some link type but different continuation

            next_link = True
            while next_link:
                try:
                    link.get(arg, **link_context)
                except HIFInputError as exception:
                    self.handle_exception(exception, link)

                # Save retrieved
                retrieved_link = deepcopy(link)
                retrieved_link.retain()
                self.links.append(retrieved_link)
                # Prepare next
                link.pk = None
                next_link = link.prepare_next()

        # Everything retrieved. We store it in results
        # link.rsl will yield either response body or the data
        # specify link.rsl behavior (and what results will be) in the link class
        if len(self.links) == 0:
            results = None
        elif len(self.links) == 1:
            link = self.links[0]
            if self.config.debug:
                self.rgs.add(link.retain())
            results = link.rsl
        else:
            results = []
            for link in self.links:
                if self.config.debug:
                    self.rgs.add(link.retain())
                if isinstance(link.rsl, dict):
                    results.append(link.rsl)
                else:  # presuming list
                    results = results + link.rsl

        # After all arguments are fetched, we store everything in self.rsl and process becomes DONE
        self.rsl = results

    class Meta:
        app_label = "core"
        proxy = True


class GroupProcess(Process, DataMixin):

    HIF_group_process = ''
    HIF_group_vary = ''

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

    def extract_task(self):
        # Every result in a group should return a Process
        # This single process could be a grouped process in turn
        for ar in self.task.results:
            ser_prc = ar.result
            self.rgs.add(ser_prc)

    def process(self):
        # Construct keyword arguments collection
        process_model = get_hif_model(self.HIF_group_process)

        processes = []
        for arg in self.args:
            process = process_model()
            config = self.config.dict(protected=True)
            config[self.HIF_group_vary] = arg
            process.setup(**config)
            processes.append(process.retain())

        # Start a task that calls class_process in multiple different ways
        grp = group(execute_process.s(False, ser_prc) for ser_prc in processes).delay()
        self.task = grp

    def post_process(self):
        rsls = self.rgs.attr('rsl', self.HIF_group_process)
        results = []
        for rsl in rsls:
            if isinstance(results, (list, tuple,)):
                results += rsl
            else:
                results.append(rsl)
        self.rsl = results

    class Meta:
        proxy = True
