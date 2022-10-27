import logging
from operator import xor
from collections.abc import Iterator

from django.apps import apps
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType
from django.core.exceptions import ValidationError

from datagrowth.datatypes import DocumentBase, CollectionBase
from datagrowth.exceptions import DGNoContent
from core.processors.base import ArgumentsTypes
from core.processors.mixins import ProcessorMixin
from core.utils.configuration import ConfigurationField
from core.utils.helpers import get_any_model
from core.exceptions import DSProcessError
from core.models.organisms import Individual, Collective


log = logging.getLogger("datagrowth.command")


class GrowthState(object):
    NEW = "New"
    PROCESSING = "Processing"
    CONTRIBUTE = "Contribute"
    COMPLETE = "Complete"
    PARTIAL = "Partial"
    ERROR = "Error"
    RETRY = "Retry"

GROWTH_STATE_CHOICES = [
    (value, value) for attr, value in sorted(GrowthState.__dict__.items()) if not attr.startswith("_")
]


class ContributeType(object):
    APPEND = "Append"
    INLINE = "Inline"
    UPDATE = "Update"

CONTRIBUTE_TYPE_CHOICES = [
    (value, value) for attr, value in sorted(ContributeType.__dict__.items()) if not attr.startswith("_")
]


PROCESS_CHOICE_LIST = [
    ("HttpResourceProcessor.fetch", "Fetch content from HTTP resource"),
    ("HttpResourceProcessor.fetch_mass", "Fetch content from multiple HTTP resources"),
    ("ExtractProcessor.extract_from_resource", "Extract content from one or more resources"),
    ("ExtractProcessor.pass_resource_through", "Take content 'as is' from one or more resources"),
]


class Growth(models.Model, ProcessorMixin):

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+", on_delete=models.PROTECT)
    community_id = models.PositiveIntegerField()

    type = models.CharField(max_length=255)
    config = ConfigurationField(
        namespace="growth",
        private=["args", "kwargs", "asynchronous"]
    )

    process = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    contribute = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST, null=True, blank=True)
    contribute_type = models.CharField(max_length=255, choices=CONTRIBUTE_TYPE_CHOICES, null=True, blank=True)

    input = GenericForeignKey(ct_field="input_type", fk_field="input_id")
    input_type = models.ForeignKey(ContentType, related_name="+", null=True, blank=True, on_delete=models.PROTECT)
    input_id = models.PositiveIntegerField(null=True, blank=True)
    output = GenericForeignKey(ct_field="output_type", fk_field="output_id")
    output_type = models.ForeignKey(ContentType, related_name="+", null=True, blank=True, on_delete=models.PROTECT)
    output_id = models.PositiveIntegerField(null=True, blank=True)

    result_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, choices=GROWTH_STATE_CHOICES, default=GrowthState.NEW, db_index=True)
    is_finished = models.BooleanField(default=False, db_index=True)

    def begin(self):  # TODO: test sample size to unlock
        """
        Starts the Celery task that provides growth of the data pool and is stored under self.process.

        :param args: (optional) The positional arguments to pass through to the process of Growth
        :param kwargs: (optional) The keyword arguments to pass through the process of Growth
        :return: the input Organism
        """
        assert self.state in [GrowthState.NEW, GrowthState.RETRY], \
            "Can't begin a growth that is in state {}".format(self.state)

        self.config = self.community.config.to_dict(protected=True)  # TODO: make this += operation instead

        processor, method, args_type = self.prepare_process(self.process, asynchronous=self.config.asynchronous)
        assert args_type == ArgumentsTypes.NORMAL and isinstance(self.input, (Individual, DocumentBase)) or \
            args_type == ArgumentsTypes.BATCH and isinstance(self.input, (Collective, CollectionBase)), \
            "Unexpected arguments type '{}' for input of class {}".format(args_type, self.input.__class__.__name__)
        args, kwargs = self.input.output(self.config.args, self.config.kwargs)
        if isinstance(self.input, (Individual, DocumentBase)):
            result = method(*args, **kwargs)
        elif isinstance(self.input, (Collective, CollectionBase)):
            if not self.config.sample_size:
                result = method(args, kwargs)
            else:
                result = method(args[:self.config.sample_size], kwargs[:self.config.sample_size])
        else:
            raise AssertionError("Growth.input is of unexpected type {}".format(type(self.input)))

        if not self.config.asynchronous:
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

        processor, method, args_type = self.prepare_process(self.process, asynchronous=self.config.asynchronous)

        if self.state == GrowthState.PROCESSING:
            try:
                result = processor.async_results(self.result_id)
                self.state = GrowthState.CONTRIBUTE
            except DSProcessError as exc:
                self.state = GrowthState.ERROR
                self.save()
                raise

        if self.state == GrowthState.CONTRIBUTE:
            scc, err = processor.results(result)
            contributions = self.prepare_contributions(scc)
            if self.contribute_type == ContributeType.APPEND:
                self.append_to_output(contributions)
            elif self.contribute_type == ContributeType.INLINE:
                assert self.config.inline_key, \
                    "No inline_key specified in configuration for Growth with inline contribution"
                self.inline_by_key(contributions, self.config.inline_key)
            elif self.contribute_type == ContributeType.UPDATE:
                assert self.config.update_key, \
                    "No update_key specified in configuration for Growth with update contribution"
                self.update_by_key(contributions, self.config.update_key)
            elif self.contribute is None:
                pass
            else:
                raise AssertionError("Growth.finish did not act on contribute_type {}".format(self.contribute_type))
            for res in err:
                res.retain(self)
            self.state = GrowthState.COMPLETE if not len(err) else GrowthState.PARTIAL
            self.save()

        return self.output, self.resources

    def prepare_contributions(self, success_resources):
        if not success_resources.exists() or not self.contribute:
            return
        contribute_processor, callback, args_type = self.prepare_process(self.contribute)
        for success_resource in success_resources.iterator():
            try:
                contribution = callback(success_resource)
                if isinstance(contribution, dict):
                    yield contribution
                elif isinstance(contribution, Iterator):
                    for contrib in contribution:
                        yield contrib
            except DGNoContent as exc:
                log.debug("No content for {} with id {}: {}".format(
                    success_resource.__class__.__name__,
                    success_resource.id,
                    exc
                ))
                success_resource.retain(self)

    def append_to_output(self, contributions):
        assert isinstance(self.output, (Collective, CollectionBase)), \
            "append_to_output expects a Collective or Collection as output"
        self.output.add(contributions)

    def inline_by_key(self, contributions, inline_key):
        assert isinstance(self.output, (Collective, CollectionBase)), \
            "inline_by_key expects a Collective or Collection as output"
        original_identifier = self.output.identifier
        assert original_identifier == inline_key, \
            "Identifier of output '{}' does not match inline key '{}'".format(original_identifier, inline_key)
        self.output.identifier = "{}.{}".format(original_identifier, original_identifier)
        self.output.save()
        for contribution in contributions:
            affected_documents = self.output.documents.filter(identity=contribution[inline_key])
            for document in affected_documents.iterator():
                document.properties[inline_key] = contribution
                document.clean()
                document.save()

    def _update_collection_by_key(self, contributions, update_key):
        for contribution in contributions:
            identifier = self.output.identifier
            assert identifier == update_key, \
                "Identifier of output '{}' does not match update key '{}'".format(identifier, update_key)
            affected_documents = self.output.documents.filter(identity=contribution[update_key])
            for document in affected_documents.iterator():
                document.update(contribution)
                document.clean()
                document.save()

    def _update_document_by_key(self, contributions, update_key):
        for contribution in contributions:
            assert update_key in self.output.properties, \
                "Output does not contain update key '{}'".format(update_key)
            self.output.update(contribution)
            self.output.clean()
            self.output.save()

    def update_by_key(self, contributions, update_key):
        if isinstance(self.output, (Collective, CollectionBase)):
            self._update_collection_by_key(contributions, update_key)
        elif isinstance(self.output, (Individual, DocumentBase)):
            self._update_document_by_key(contributions, update_key)
        else:
            raise AssertionError("update_by_key expects a Collective/Collection or Individual/Document as output")

    def save(self, *args, **kwargs):
        self.is_finished = self.state in [GrowthState.COMPLETE, GrowthState.PARTIAL]
        super(Growth, self).save(*args, **kwargs)

    def clean(self):
        if xor(bool(self.contribute_type), bool(self.contribute)):
            raise ValidationError(
                "Contribution is partially specified "
                "with a type of {} and a value of {}".format(self.contribute_type, self.contribute)
            )

    @property
    def resources(self):
        Resource = apps.get_model(self.config.resource)
        Type = ContentType.objects.get_for_model(self)
        return Resource.objects.filter(retainer_type__pk=Type.id, retainer_id=self.id)

    def __str__(self):
        return "{} growth for {}".format(
            self.type,
            self.community
        )

    class Meta:
        get_latest_by = "id"
        ordering = ("id",)
