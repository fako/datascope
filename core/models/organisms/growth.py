from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.db import models

from datascope.configuration import PROCESS_CHOICE_LIST
from core.models.organisms.community import Community
from core.utils.configuration import ConfigurationField


class GrowthState(object):
    NEW = "New"
    PROCESSING = "Processing"
    FINISHED = "Finished"
    ERROR = "Error"
    RETRY = "Retry"

GROWTH_STATE_CHOICES = [
    (attr, value) for attr, value in six.iteritems(GrowthState.__dict__) if not attr.startswith("_")
]


class Growth(models.Model):

    #community = models.ForeignKey(Community)

    type = models.CharField(max_length=255)
    input = models.CharField(max_length=255)
    config = ConfigurationField()

    process = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    success = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    output = models.CharField(max_length=255)

    task_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, choices=GROWTH_STATE_CHOICES, default=GrowthState.NEW)
    is_finished = models.BooleanField(default=False)

    def begin(self, *args, **kwargs):
        """
        Starts the Celery tasks according to model fields and external arguments to enable growth.

        :param args: (optional)
        :return: the input Organism

        - Initializes a process
        - Passes args and kwargs to delay of specified attribute, which is assumed to be a subtask
        - Stores resulting task_id and sets state
        """
        pass

    def finish(self):
        """
        Takes results from self.results and creates an Organism according to ContentType stored in self.output.
        It stores a reference to the new Organism in self.output and returns it.
        Will ignore any errors that are not specified in self.errors and

        :return: the output Organism
        - Revives the process and calls get_results
        - Runs the success process for every success
        - Fills output with results from success process
        - Returns the output as well as the (unprocessed) errors
        """
        pass

    def create_processor(self, processor, config):
        """
        Creates an instance of process based on self.process, self.config and args

        :param args:
        :param kwargs: (optional)
        :return:
        """
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod
        pass

    @property
    def progress(self):
        """
        Tries to load the task_id as AsyncResult or GroupResult and indicates task progress.

        :return:
        """
        return None

    @property
    def results(self):  # TODO: make this class iterable
        """
        Returns a Storage class and all ids that were created for the growth

        :return:
        """
        return None

    def save(self, *args, **kwargs):
        self.is_finished = self.state == GrowthState.FINISHED
        super(Growth, self).save(*args, **kwargs)