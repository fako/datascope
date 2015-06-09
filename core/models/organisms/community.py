from __future__ import unicode_literals, absolute_import, print_function, division
import six

from collections import OrderedDict

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation, ContentType

from datascope.configuration import DEFAULT_CONFIGURATION
from core.models.organisms import Growth, Collective, Individual
from core.models.user import DataScopeUser
from core.utils.configuration import ConfigurationField
from core.utils.helpers import get_any_model


class CommunityManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        super(CommunityManager, self).get_queryset(*args, **kwargs).select_related(
            "current_growth"
        )


class Community(models.Model):
    """

    """
    #user = models.ForeignKey(DataScopeUser, null=True)
    #predecessor = models.ForeignKey('Community', null=True)

    identity = models.CharField(max_length=255)
    config = ConfigurationField(
        config_defaults=DEFAULT_CONFIGURATION
    )

    growth_set = GenericRelation(Growth, content_type_field="community_type", object_id_field="community_id")
    collective_set = GenericRelation(Collective, content_type_field="community_type", object_id_field="community_id")
    individual_set = GenericRelation(Individual, content_type_field="community_type", object_id_field="community_id")

    current_growth = models.ForeignKey('Growth', null=True)
    kernel = GenericForeignKey(ct_field="kernel_type", fk_field="kernel_id")
    kernel_type = models.ForeignKey(ContentType, null=True)
    kernel_id = models.PositiveIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    views = models.IntegerField(default=1)
    state = models.CharField(max_length=255)  # TODO: set choices

    COMMUNITY_SPIRIT = OrderedDict()
    COMMUNITY_BODY = []

    @classmethod
    def get_or_create_by_input(cls, *args, **kwargs):
        # TODO: implement
        pass

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

    def setup_growth(self):
        """
        Will create all Growth objects based on the community_spirit
        """
        for growth_type, growth_config in six.iteritems(self.COMMUNITY_SPIRIT):
            sch = growth_config["schema"]
            cnf = growth_config["config"]
            prc = growth_config["process"]
            cont, con = growth_config["contribute"].split(":")
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
                inp = self.initial_input()
            if out.startswith("@"):
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
        raise NotImplementedError()

    def initial_input(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: Collective or Individual
        """
        raise NotImplementedError()

    def grow(self):
        """

        :return:
        """
        assert self.id, "A community can only be grown after an initial save."

        if self.current_growth is None:
            self.setup_growth()
            self.current_growth = self.next_growth()
            self.call_begin_callback(self.current_growth.type, self.current_growth.input)
            self.current_growth.begin()
        if self.current_growth.is_finished:
            return


        # FEATURE: wrap rest of function in while True for synchronous handling
        output, errors = self.current_growth.finish()  # will raise when Growth is not finished
        self.call_finish_callback(self.current_growth.type, output, errors)
        try:
            self.current_growth = self.next_growth()
        except Growth.DoesNotExist:
            self.set_kernel()
            self.save()
            return
        self.call_begin_callback(self.current_growth.type, self.current_growth.input)
        self.current_growth.begin()
        self.save()

    def manifestation(self):
        """
        Return content of the self.kernel processed through self.contribution.

        :return:
        """
        pass

    class Meta:
        abstract = True
