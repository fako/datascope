from __future__ import unicode_literals, absolute_import, print_function, division
import six

import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from datascope.configuration import PROCESS_CHOICE_LIST, DEFAULT_CONFIGURATION
from core.utils.configuration import ConfigurationField
from core.utils.helpers import get_any_model
from core.exceptions import DSProcessError, DSNoContent
from core.models.organisms import Individual, Collective
from core.models.organisms.mixins import ProcessorMixin


log = logging.getLogger("datascope")


class GrowthState(object):
    NEW = "New"
    PROCESSING = "Processing"
    CONTRIBUTE = "Contribute"
    COMPLETE = "Complete"
    PARTIAL = "Partial"
    ERROR = "Error"
    RETRY = "Retry"

GROWTH_STATE_CHOICES = [
    (value, value) for attr, value in six.iteritems(GrowthState.__dict__) if not attr.startswith("_")
]


class ContributeType(object):
    APPEND = "Append"

CONTRIBUTE_TYPE_CHOICES = [
    (value, value) for attr, value in six.iteritems(ContributeType.__dict__) if not attr.startswith("_")
]


class Growth(models.Model, ProcessorMixin):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    type = models.CharField(max_length=255)
    config = ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION,
        namespace="growth",
        private=["args", "kwargs", "async"]
    )

    process = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    contribute = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    contribute_type = models.CharField(max_length=255, choices=CONTRIBUTE_TYPE_CHOICES)

    input = GenericForeignKey(ct_field="input_type", fk_field="input_id")
    input_type = models.ForeignKey(ContentType, related_name="+", null=True)
    input_id = models.PositiveIntegerField(null=True)
    output = GenericForeignKey(ct_field="output_type", fk_field="output_id")
    output_type = models.ForeignKey(ContentType, related_name="+")
    output_id = models.PositiveIntegerField()

    result_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, choices=GROWTH_STATE_CHOICES, default=GrowthState.NEW, db_index=True)
    is_finished = models.BooleanField(default=False, db_index=True)

    def begin(self):
        """
        Starts the Celery task that provides growth of the data pool and is stored under self.process.

        :param args: (optional) The positional arguments to pass through to the process of Growth
        :param kwargs: (optional) The keyword arguments to pass through the process of Growth
        :return: the input Organism
        """
        assert self.state in [GrowthState.NEW, GrowthState.RETRY], \
            "Can't begin a growth that is in state {}".format(self.state)

        self.config = self.community.config.to_dict(protected=True)  # TODO: make this += operation instead

        processor, method = self.prepare_process(self.process, async=self.config.async)  # TODO: unit test async
        args, kwargs = self.input.output(self.config.args, self.config.kwargs)
        if isinstance(self.input, Individual):
            result = method(*args, **kwargs)
        elif isinstance(self.input, Collective):
            result = method(args, kwargs)
        else:
            raise AssertionError("Growth.input is of unexpected type {}".format(type(self.input)))

        if not self.config.async:
            self.state = GrowthState.CONTRIBUTE
        else:
            self.state = GrowthState.PROCESSING
            self.result_id = result.id
        self.save()
        return result

    def finish(self, result):
        """

        :return: the output Organism and unprocessed errors
        """
        assert self.state in [
            GrowthState.PROCESSING, GrowthState.COMPLETE, GrowthState.PARTIAL, GrowthState.CONTRIBUTE
        ], "Can't finish a growth that is in state {}".format(self.state)

        processor, method = self.prepare_process(self.process, async=self.config.async)

        if self.state == GrowthState.PROCESSING:
            try:
                result = processor.async_results(self.result_id)
                self.state = GrowthState.CONTRIBUTE
            except DSProcessError as exc:
                self.state = GrowthState.ERROR
                self.save()
                raise exc  # TODO: reraise?

        if self.state == GrowthState.CONTRIBUTE:
            scc, err = processor.results(result)
            if self.contribute_type == ContributeType.APPEND:
                self.append_to_output(scc)
            else:
                raise AssertionError("Growth.finish did not act on contribute_type {}".format(self.contribute_type))
            for res in err:
                res.retain(self)
            self.state = GrowthState.COMPLETE if not len(err) else GrowthState.PARTIAL
            self.save()

        return self.output, self.resources

    def append_to_output(self, contributions):
        contribute_processor, callback = self.prepare_process(self.contribute)
        results = []
        for contribution in contributions:
            try:
                results += callback(contribution)
            except DSNoContent as exc:
                log.debug("No content for {} with id {}: {}".format(
                    contribution.__class__.__name__,
                    contribution.id,
                    exc
                ))
                contribution.retain(self)
        self.output.update(results)

    def save(self, *args, **kwargs):
        self.is_finished = self.state in [GrowthState.COMPLETE, GrowthState.PARTIAL]
        super(Growth, self).save(*args, **kwargs)

    @property
    def resources(self):
        Resource = get_any_model(self.config.resource)
        Type = ContentType.objects.get_for_model(self)
        return Resource.objects.filter(retainer_type__pk=Type.id, retainer_id=self.id)
