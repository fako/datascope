import six

from itertools import groupby
from collections import OrderedDict, Iterator
import logging

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation, ContentType

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms.states import CommunityState, COMMUNITY_STATE_CHOICES
from core.models.organisms import Growth, Collective, Individual, Organism
from core.models.organisms.managers.community import CommunityManager
from core.models.resources.manifestation import Manifestation
from core.models.user import DataScopeUser
from core.processors.mixins import ProcessorMixin
from core.utils.configuration import ConfigurationField
from core.utils.helpers import get_any_model
from core.exceptions import DSProcessUnfinished, DSProcessError


log = logging.getLogger("datascope")


class Community(models.Model, ProcessorMixin):
    """

    """
    #user = models.ForeignKey(DataScopeUser, null=True)
    #predecessor = models.ForeignKey('Community', null=True)

    signature = models.CharField(max_length=255, db_index=True)
    config = ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION
    )

    growth_set = GenericRelation(Growth, content_type_field="community_type", object_id_field="community_id")
    collective_set = GenericRelation(Collective, content_type_field="community_type", object_id_field="community_id")
    individual_set = GenericRelation(Individual, content_type_field="community_type", object_id_field="community_id")
    manifestation_set = GenericRelation(Manifestation, content_type_field="community_type", object_id_field="community_id")

    current_growth = models.ForeignKey('core.Growth', null=True)
    kernel = GenericForeignKey(ct_field="kernel_type", fk_field="kernel_id")
    kernel_type = models.ForeignKey(ContentType, null=True, blank=True)
    kernel_id = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    views = models.IntegerField(default=0)
    state = models.CharField(max_length=255, choices=COMMUNITY_STATE_CHOICES, default=CommunityState.NEW)

    COMMUNITY_SPIRIT = OrderedDict()
    COMMUNITY_BODY = []
    ASYNC_MANIFEST = False
    INPUT_THROUGH_PATH = True
    PUBLIC_CONFIG = {}
    SAMPLE_SIZE = 0

    objects = CommunityManager()

    @classmethod
    def get_signature_from_input(cls, *args, **kwargs):
        signature = list(args) + [
            "{}={}".format(key, value)
            for key, value in six.iteritems(kwargs)
            if key in cls.PUBLIC_CONFIG and not key.startswith("$")
        ]
        signature = list(filter(bool, signature))
        signature.sort()
        return "&".join(signature)

    @classmethod
    def get_configuration_from_input(cls, *args, **kwargs):
        return {key: value for key, value in six.iteritems(kwargs) if key in cls.PUBLIC_CONFIG}

    def call_finish_callback(self, phase, out, errors):
        callback_name = "finish_" + phase
        callback = getattr(self, callback_name, None)
        if callback is not None and callable(callback):
            callback(out, errors)

    def call_begin_callback(self, phase, inp):
        callback_name = "begin_" + phase
        callback = getattr(self, callback_name, None)
        if callback is not None and callable(callback):
            callback(inp)

    def call_error_callbacks(self, phase, errors, out):
        errors.order_by('-status')
        phase_config = self.COMMUNITY_SPIRIT[phase]
        error_config = phase_config["errors"]
        if error_config is None:
            return True
        fatal_error = not out.has_content
        for status, error_group in groupby(errors, lambda err: err.status):
            if status in error_config:
                callback_name = "error_{}_{}".format(phase, error_config[status])
                callback = getattr(self, callback_name, None)
                if callback is not None and callable(callback):
                    should_continue = callback(list(error_group), out)
                    fatal_error = fatal_error or not should_continue
        return not fatal_error

    def call_manifestation_callbacks(self, manifestation_part):
        callback_name = "before_{}_manifestation".format(manifestation_part.get("name", ""))
        callback = getattr(self, callback_name, None)
        if callback is not None and callable(callback):
            callback(manifestation_part)

    def create_organism(self, organism_type, schema, identifier=None):
        model = get_any_model(organism_type)
        org = model(community=self, schema=schema)
        if identifier and hasattr(org, "identifier"):
            org.identifier = identifier
        org.save()
        return org

    def setup_growth(self, *args):
        """
        Will create all Growth objects based on the community_spirit
        """
        for growth_type, growth_config in six.iteritems(self.COMMUNITY_SPIRIT):
            sch = growth_config["schema"]
            cnf = self.config.to_dict(protected=True)
            if self.SAMPLE_SIZE:
                cnf["sample_size"] = self.SAMPLE_SIZE
            cnf.update(growth_config["config"])
            prc = growth_config["process"]
            if growth_config["contribute"]:
                cont, con = growth_config["contribute"].split(":")
            else:
                cont, con = None, None

            inp = growth_config["input"]
            if inp is not None and inp.startswith("@"):
                grw = self.growth_set.filter(type=inp[1:]).last()
                if grw is None:
                    raise AssertionError(
                        "Could not find growth with type {} for input of {}".format(inp[1:], growth_type)
                    )
                inp = grw.output
            elif inp is None:
                inp = self.initial_input(*args)
            elif inp.startswith("Collective"):
                if "#" in inp:
                    inp, identifier = inp.split("#")
                else:
                    identifier = None
                inp = self.create_organism(inp, sch, identifier)
                inp.identifier = identifier
            elif inp == "Individual":
                inp = self.create_organism(inp, sch)

            out = growth_config["output"]

            if out is None:
                pass
            elif out.startswith("@"):
                grw = self.growth_set.filter(type=out[1:]).last()
                if grw is None:
                    raise AssertionError(
                        "Could not find growth with type {} for output of {}".format(out[1:], growth_type)
                    )
                out = grw.output
            elif out == "&input":
                out = inp
            elif out.startswith("Collective"):
                if "#" in out:
                    out, identifier = out.split("#")
                else:
                    identifier = None
                out = self.create_organism(out, sch, identifier)
                out.identifier = identifier
            elif out == "Individual":
                out = self.create_organism(out, sch)
            else:
                raise AssertionError("Invalid value for output: {}".format(out))
            growth = Growth(
                community=self,
                type=growth_type,
                config=cnf,
                process=prc,
                contribute=con,
                contribute_type=cont,
                input=inp,
                output=out
            )
            growth.clean()
            growth.save()

    def next_growth(self):
        growth = self.growth_set.filter(is_finished=False).first()
        if growth is None:
            raise Growth.DoesNotExist("Community.next_growth did not find a next growth.")
        return growth

    def get_growth(self, phase):
        return self.growth_set.filter(type=phase).last()

    def set_kernel(self):
        """

        :return:
        """
        assert self.kernel is not None, \
            "Community.set_kernel expected the kernel to be set. " \
            "The overriding method is failing, is not implemented or is calling its parent before the kernel is set."
        assert issubclass(self.kernel.__class__, Organism), \
            "The kernel should be an Organism."

    def initial_input(self, *args):
        """

        :param args:
        :param kwargs:
        :return: Collective or Individual
        """
        raise NotImplementedError()

    def grow(self, *args):
        """

        :return:
        """
        assert self.id, "A community can only be grown after an initial save."
        args = args or []

        if self.state == CommunityState.READY:
            return True
        elif self.state == CommunityState.SYNC:
            return False

        result = None
        if self.state in [CommunityState.NEW]:
            log.info("Preparing community")
            self.state = CommunityState.ASYNC if self.config.async else CommunityState.SYNC
            self.setup_growth(*args)
            self.current_growth = self.next_growth()
            self.save()  # in between save because next operations may take long and community needs to be claimed.
            log.info("Preparing " + self.current_growth.type)
            self.call_begin_callback(self.current_growth.type, self.current_growth.input)
            log.info("Starting " + self.current_growth.type)
            result = self.current_growth.begin()  # when synchronous result contains actual results
            self.save()

        while self.kernel is None:

            output, errors = self.current_growth.finish(result)  # will raise when Growth is not finished
            error_count = errors.count()
            if error_count > 1:
                should_finish = self.call_error_callbacks(self.current_growth.type, errors, output)
                log.info("{} errors occurred".format(error_count))
            else:
                should_finish = True
            if not should_finish:
                self.state = CommunityState.ABORTED
                self.save()
                raise DSProcessError("Could not finish growth according to error callbacks.")
            log.info("Finishing " + self.current_growth.type)
            self.call_finish_callback(self.current_growth.type, output, errors)
            try:
                self.current_growth = self.next_growth()
            except Growth.DoesNotExist:
                self.set_kernel()
                self.state = CommunityState.READY
                self.save()
                return True
            log.info("Preparing " + self.current_growth.type)
            self.call_begin_callback(self.current_growth.type, self.current_growth.input)
            log.info("Starting " + self.current_growth.type)
            result = self.current_growth.begin()
            self.save()

            if self.state == CommunityState.ASYNC:
                raise DSProcessUnfinished("Community starts another Growth.")

    @property
    def manifestation(self):
        """
        Return content of the self.kernel processed through self.contribution.

        :return:
        """
        content = self.kernel.content
        for part in self.COMMUNITY_BODY:
            self.call_manifestation_callbacks(part)
            processor, method, args_type = self.prepare_process(part["process"], extra_config=part.get("config"))
            content = method(content)
            assert isinstance(content, Iterator), \
                "To prevent high memory usage processors should return iterators when manifestating"
        return content

    @classmethod
    def get_name(cls):
        if hasattr(cls, 'COMMUNITY_NAME'):
            return cls.COMMUNITY_NAME
        word_separator = '_'
        class_name = cls.__name__
        class_name = class_name.replace('Community', '')
        name = ''
        for index, char in enumerate(class_name):
            if char.isupper():
                name += word_separator + char.lower() if not index == 0 else char.lower()
            else:
                name += char
        return name

    def __str__(self):
        return "{} ({}, {})".format(
            self.signature,
            self.id,
            self.state
        )

    class Meta:
        abstract = True
        get_latest_by = "created_at"
