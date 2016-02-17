from __future__ import unicode_literals, absolute_import, print_function, division
import six
from django.utils.encoding import python_2_unicode_compatible

from collections import OrderedDict
from datetime import datetime

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation, ContentType

from celery.result import AsyncResult
from json_field import JSONField

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms import Growth, Collective, Individual, Organism
from core.models.organisms.mixins import ProcessorMixin
from core.models.user import DataScopeUser
from core.utils.configuration import ConfigurationField
from core.utils.helpers import get_any_model
from core.tasks import manifest_community
from core.exceptions import DSProcessUnfinished


class CommunityState(object):
    NEW = "New"
    ASYNC = "Asynchronous"
    SYNC = "Synchronous"
    READY = "Ready"

COMMUNITY_STATE_CHOICES = [
    (value, value) for attr, value in six.iteritems(CommunityState.__dict__) if not attr.startswith("_")
]


@python_2_unicode_compatible
class Manifestation(models.Model):

    uri = models.CharField(max_length=255, db_index=True, default=None)
    data = JSONField(null=True)
    config = ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION
    )

    community = GenericForeignKey(ct_field="community_type", fk_field="community_id")
    community_type = models.ForeignKey(ContentType, related_name="+")
    community_id = models.PositiveIntegerField()

    task = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def generate_config(allowed_config, **kwargs):
        config = {key: value for key, value in six.iteritems(kwargs) if key in allowed_config}
        return config

    def get_data(self):
        if self.data:
            return self.data
        if self.task:
            result = AsyncResult(self.task)
            if not result.ready():
                raise DSProcessUnfinished("Manifest processing is not done")
            self.data = result.result
            self.completed_at = datetime.now()
            self.save()
            return self.data
        if self.community.ASYNC_MANIFEST:
            self.task = manifest_community.delay(self.id)
            self.save()
            raise DSProcessUnfinished("Manifest started processing")
        else:
            return manifest_community(self.id)

    def __str__(self):
        return "Manifestation {} for {}".format(
            self.id,
            self.community
        )


@python_2_unicode_compatible
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

    current_growth = models.ForeignKey('Growth', null=True)
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

    @classmethod
    def get_or_create_by_input(cls, *args, **kwargs):
        signature = list(args) + [
            "{}={}".format(key, value)
            for key, value in six.iteritems(kwargs)
            if key in cls.PUBLIC_CONFIG and not key.startswith("$")
        ]
        signature = filter(bool, signature)
        signature.sort()
        created = False
        try:
            community = cls.objects.get(signature="&".join(signature))
        except cls.DoesNotExist:
            community = cls(
                signature="&".join(signature),
                config={key: value for key, value in six.iteritems(kwargs) if key in cls.PUBLIC_CONFIG}
            )
            community.save()
            created = True
        return community, created

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

    def create_organism(self, organism_type, schema):
        model = get_any_model(organism_type)
        org = model(community=self, schema=schema)
        org.save()
        return org

    def setup_growth(self, *args):
        """
        Will create all Growth objects based on the community_spirit
        """
        for growth_type, growth_config in six.iteritems(self.COMMUNITY_SPIRIT):
            sch = growth_config["schema"]
            cnf = growth_config["config"]
            prc = growth_config["process"]
            if growth_config["contribute"]:
                cont, con = growth_config["contribute"].split(":")
            else:
                cont, con = None, None
            inp = growth_config["input"]
            out = growth_config["output"]
            if inp is not None and inp.startswith("@"):
                grw = self.growth_set.filter(type=inp[1:]).last()
                if grw is None:
                    raise AssertionError(
                        "Could not find growth with type {} for input of {}".format(inp[1:], growth_type)
                    )
                inp = grw.output
            elif inp is None:
                inp = self.initial_input(*args)
            if out is not None and out.startswith("@"):
                grw = self.growth_set.filter(type=out[1:]).last()
                if grw is None:
                    raise AssertionError(
                        "Could not find growth with type {} for output of {}".format(out[1:], growth_type)
                    )
                out = grw.output
            if inp in ["Individual", "Collective"]:
                inp = self.create_organism(inp, sch)
            if out in ["Individual", "Collective"]:
                out = self.create_organism(out, sch)
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
            growth.save()

    def next_growth(self):
        growth = self.growth_set.filter(is_finished=False).first()
        if growth is None:
            raise Growth.DoesNotExist("Community.next_growth did not find a next growth.")
        return growth

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
            self.state = CommunityState.ASYNC if self.config.async else CommunityState.SYNC
            self.setup_growth(*args)
            self.current_growth = self.next_growth()
            self.save()  # in between save because next operations may take long and community needs to be claimed.
            self.call_begin_callback(self.current_growth.type, self.current_growth.input)
            result = self.current_growth.begin()  # when synchronous result contains actual results
            self.save()

        while self.kernel is None:

            output, errors = self.current_growth.finish(result)  # will raise when Growth is not finished
            self.call_finish_callback(self.current_growth.type, output, errors)
            try:
                self.current_growth = self.next_growth()
            except Growth.DoesNotExist:
                self.set_kernel()
                self.state = CommunityState.READY
                self.save()
                return True
            self.call_begin_callback(self.current_growth.type, self.current_growth.input)
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
            processor, method = self.prepare_process(part["process"])
            content = method(content)
        return content

    @classmethod
    def get_name(cls):
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
