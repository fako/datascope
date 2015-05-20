from django.db import models

import jsonfield

from ..user import DataScopeUser


class CommunityManager(models.Manager):

    def get_queryset(self):  # TODO: good? bad?
        return super(CommunityManager, self).get_queryset().prefetch_related(
            'individuals',
            'collectives',
            'growths'
        )


class Community(models.Model):
    """
    NB: When fetching a community it is recommended to prefetch Individuals, Collectives and Growths with it
    TODO: Create a SpiritField or SpiritPhase class which manages a spirit phase
    """
    default_configuration = {
        "depth": 0
    }
    user = models.ForeignKey(DataScopeUser, null=True)
    predecessor = models.ForeignKey('Community', null=True)

    enlightened = models.BooleanField(default=False)
    data = jsonfield.JSONField(null=True, blank=True)

    path = models.CharField(max_length=255, db_index=True)
    config = jsonfield.JSONField(db_index=True)  # TODO: should become a ConfigurationField

    # TODO: add created_at etc.
    # TODO: add view count

    def capture_initial_input(self, config, *args, **kwargs):
        """
        For visual-translations this would return a Collective with {"locale": X, "query": Y} Individuals.
        Their spirits should be init-Y-X and init-Y for the Collective

        :param args:
        :param kwargs:
        :return: Collective or Individual
        """
        return None

    def get_collective_from_path(self, path):
        """
        Parse a path and return the collective that belongs to that path.
        If a JSON path is specified after the hash, it will return a list of values present at that path.

        :param path:
        :return:
        """
        pass

    def grow(self, config, *args, **kwargs):
        """

        :return:

        - If enlightened property is set: exit
        - Look for latest Growth
        - Calls Growth.progress
        - If no progress: exit
        - Fetch results
        - Create Collective or Individual from the results
        - Call Community.after_PHASE (optional)
        - If there is no new phase: exit
        - Go to next phase
        - Call Community.before_PHASE (optional)
        - Start new growth
        - If no more growth: set enlightened to True
        """
        if self.enlightened:
            return

    def create_growth(self, spirit_phase):
        """
        Creates a Growth based on spirit_phase and returns it.

        :param spirit_phase:
        :return: Growth
        """
        pass

    @property
    def kernel(self):
        """
        Returns the spirit of the Individual or Collective that is the base for results. Override this method in subclasses.

        :return: None
        """
        return None

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
        unique_together = ('path', 'config')