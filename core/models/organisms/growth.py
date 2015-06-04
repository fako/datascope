from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.apps import apps as django_apps
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

import core.processors
from datascope.configuration import PROCESS_CHOICE_LIST
from core.models.organisms.community import Community
from core.utils.configuration import ConfigurationField
from core.exceptions import DSProcessError


class GrowthState(object):
    NEW = "New"
    PROCESSING = "Processing"
    FINISHED = "Finished"
    PARTIAL = "Partial"
    ERROR = "Error"
    RETRY = "Retry"

GROWTH_STATE_CHOICES = [
    (attr, value) for attr, value in six.iteritems(GrowthState.__dict__) if not attr.startswith("_")
]


class ContributeType(object):
    APPEND = "Append"

CONTRIBUTE_TYPE_CHOICES = [
    (attr, value) for attr, value in six.iteritems(ContributeType.__dict__) if not attr.startswith("_")
]


class Growth(models.Model):

    #community = models.ForeignKey(Community)

    type = models.CharField(max_length=255)
    config = ConfigurationField()

    process = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    contribute = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    contribute_type = models.CharField(max_length=255, choices=CONTRIBUTE_TYPE_CHOICES)

    input = GenericForeignKey(ct_field="input_type", fk_field="input_id")
    input_type = models.ForeignKey(ContentType, related_name="+")
    input_id = models.PositiveIntegerField()
    output = GenericForeignKey(ct_field="output_type", fk_field="output_id")
    output_type = models.ForeignKey(ContentType, related_name="+")
    output_id = models.PositiveIntegerField()

    result_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, choices=GROWTH_STATE_CHOICES, default=GrowthState.NEW, db_index=True)
    is_finished = models.BooleanField(default=False, db_index=True)

    def begin(self, *args, **kwargs):
        """
        Starts the Celery task that provides growth of the data pool and is stored under self.process.

        :param args: (optional) The positional arguments to pass through to the process of Growth
        :param kwargs: (optional) The keyword arguments to pass through the process of Growth
        :return: the input Organism
        """
        assert self.state in [GrowthState.NEW, GrowthState.RETRY], \
            "Can't begin a growth that is in state {}".format(self.state)

        processor, method = self.prepare_process(self.process)
        task = getattr(processor, method)
        result = task.delay(*args, **kwargs)
        self.result_id = result.id
        self.state = GrowthState.PROCESSING
        self.save()

    def finish(self):
        """

        :return: the output Organism and unprocessed errors
        """
        assert self.state in [GrowthState.PROCESSING, GrowthState.FINISHED, GrowthState.PARTIAL], \
            "Can't finish a growth that is in state {}".format(self.state)

        if self.state in [GrowthState.PROCESSING]:
            processor, method = self.prepare_process(self.process)
            try:
                successes, errors = processor.get_results(self.result_id)
            except DSProcessError as exc:
                self.state = GrowthState.ERROR
                self.save()
                raise exc  # TODO: reraise?
            if self.contribute_type == ContributeType.APPEND:
                self.append_to_output(successes)
            else:
                raise AssertionError("Growth.finish did not act on contribute_type {}".format(self.contribute_type))
            for error in errors:
                error.retain(self)
            self.state = GrowthState.FINISHED if not len(errors) else GrowthState.PARTIAL
            self.save()
        return self.output, self.resources

    def append_to_output(self, contributions):
        contribute_processor, contribute_method = self.prepare_process(self.contribute)
        results = []
        for contribution in contributions:
            callback = getattr(contribute_processor, contribute_method)
            results += callback(contribution)
        self.output.update(results)

    def prepare_process(self, process):
        """
        Creates an instance of the processor based on requested process with a correct config set.
        Processors get loaded from core.processors
        It returns the processor and the method that should be invoked.

        :param process: A dotted string indicating the processor and method that represent the process.
        :return: processor, method
        """
        processor_name, method_name = process.split(".")
        try:
            processor_class = getattr(core.processors, processor_name)
        except AttributeError:
            raise AssertionError(
                "Could not import a processor named {} from core.processors".format(processor_name)
            )
        processor = processor_class(config=self.config.to_dict(protected=True))
        return processor, method_name

    def save(self, *args, **kwargs):
        self.is_finished = self.state == GrowthState.FINISHED
        super(Growth, self).save(*args, **kwargs)

    @property
    def resources(self):
        Resource = django_apps.get_model("sources", self.config.resource)
        Type = ContentType.objects.get_for_model(self)
        return Resource.objects.filter(retainer_type__pk=Type.id, retainer_id=self.id)
