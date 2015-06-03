from __future__ import unicode_literals, absolute_import, print_function, division

from collections import OrderedDict

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey

import jsonfield

from core.models.user import DataScopeUser


class CommunityManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        super(CommunityManager, self).get_queryset(*args, **kwargs).select_related(
            "current_growth"
        )


class CommunitySpirit(object):
    def setup_growth(self):
        """
        Will create all Growth objects based on the community_spirit
        """
        pass

    def next_growth(self):
        """
        Returns the first is_finished=False Growth on the community
        """
        pass


class Community(models.Model):
    """

    """
    user = models.ForeignKey(DataScopeUser, null=True)
    predecessor = models.ForeignKey('Community', null=True)

    config = jsonfield.JSONField(db_index=True)  # TODO: should become a ConfigurationField

    current_growth = models.ForeignKey('Growth', null=True)
    kernel = GenericForeignKey(ct_field="kernel_type", fk_field="kernel_id")
    kernel_type = models.CharField(max_length=255, null=True)
    kernel_id = models.PositiveIntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    purge_at = models.DateTimeField(null=True, blank=True)

    views = models.IntegerField(default=1)
    state = models.CharField(max_length=255)  # TODO: set choices

    COMMUNITY_SPIRIT = OrderedDict()
    COMMUNITY_BODY = []

    @property
    def spirit(self):
        return None
    @spirit.setter
    def spirit(self, community_spirit):
        pass

    def set_kernel(self):
        """

        :return:
        """
        pass

    def capture_initial_input(self, *args, **kwargs):
        """
        For visual-translations this would return a Collective with {"locale": X, "query": Y} Individuals.
        Their spirits should be init-Y-X and init-Y for the Collective

        :param args:
        :param kwargs:
        :return: Collective or Individual
        """
        return None

    def grow(self, *args, **kwargs):
        """

        :return:

        - If there is no current_growth: spirit.setup_growth(); spirit.next_growth(); growth.begin()
        - If current_growth.is_finished: exit
        - Calls current_growth.finish which raises on not ready or error

        - Call Community.error_PHASE_X(errors, output) for erroneous results
        - Call Community.finish_PHASE (optional)
        - current_growth = spirit.next_growth() under try statement
        - If there is no next growth: self.set_kernel(); exit
        - Call Community.begin_PHASE (optional)
        - current_growth.begin()
        - raise in progress
        """
        if self.enlightened:
            return

    def results(self, depth=None):
        """
        Return content of the self.kernel Individual or Collective.

        :param depth: (optional) indicates the level of recursion that should be used to inline nested Individuals and or Collectives.
        :return:
        """
        # TODO: should set a default depth from self.config
        pass

    def load_organism_from_spirit(self, json_path):
        """
        Query Organism assigned to key at json_path.

        :param json_path:
        :return:
        """

    class Meta:
        abstract = True
