from collections import OrderedDict

from django.db import models

from jsonfield import JSONField


class Organism(models.Model):
    community = models.ForeignKey('Community')
    schema = JSONField()
    spirit = models.CharField(max_length=255, db_index=True)

    @classmethod  # TODO: write manager instead!
    def create_from_json(cls, json_string, schema, context=None):
        """
        Parses the json string into a data structure
        and then adds dictionaries inside a newly created Collective if any validates against the schema.
        The matching dictionaries will be stored as Individual. If the context parameter is set to a dictionary.
        The Individuals get updated with the given dictionary.

        :param json_string:
        :param schema:
        :param context:
        :return:
        """
        pass

    @classmethod  # TODO: write manager instead!
    def create_from_growth(cls, growth):
        """

        :param growth:
        :return:
        """
        pass

    def add_from_growth(self, growth):
        """

        :param growth:
        :return:
        """
        pass

    def add_from_json(self, json_string, schema, context=None):
        """
        Parses the json string into a data structure and then adds dictionaries to self if any validates against the schema.
        The matching dictionaries will be stored as Individual. If the context parameter is set to a dictionary.
        The Individuals get updated with the given dictionary.

        :param json_string:
        :param schema:
        :param context:
        :return:
        """
        pass

    @property
    def url(self, json_path=None):
        """
        TODO: Uses Django reverse
        Sets an anchor if json_path is given

        :param json_path: (optional)
        :return:
        """
        if not self.id:
            raise ValueError("Can't get path for unsaved Collective")
        return "ind|col/{}/".format(self.id)

    @property
    def content(self):
        """
        Return the content of the instance. This property is meant to be overridden by subclasses.

        :return: None
        """
        return None

    class Meta:
        abstract = True
        unique_together = ('community_id', 'spirit')


class Individual(Organism):

    collective = models.ForeignKey('Collective', null=True)
    properties = JSONField()

    def __getattr__(self, item):
        return getattr(self.properties, item)

    @classmethod  # TODO: write manager instead!
    def create_from_dict(cls, dic, schema):
        """
        Create new instance of this class from a dictionary if it validates against the schema.

        :param dic:
        :param schema:the schema to validate against
        :return:
        """
        pass

    def update_from_dict(self, dic):
        """
        Override existing properties with values from dic if it validates against the schema.

        :param dic:
        :return:
        """
        pass

    @property
    def content(self):
        """
        Returns the content of this Individual

        :return: properties dictionary
        """
        return self.properties


class Collective(Organism):

    @classmethod  # TODO: write manager instead!
    def create_from_list(cls, lst, schema, context=None):
        """
        Create new instance of this class from list if any dictionary inside validates against the schema.
        The matching dictionaries will be stored as Individual. If the context parameter is set to a dictionary.
        The Individuals get updated with the given dictionary.

        :param lst:
        :param schema:
        :param context: (optional)
        :return:
        """
        pass

    def add_from_list(self, lst, context=None):
        """
        Adds any dictionaries in list as Individual to this class if they validate against set schema.
        If the context parameter is set to a dictionary. The Individuals get updated with the given dictionary.

        :param lst:
        :param context: (optional)
        :return:
        """
        pass

    def list_json_path(self, json_path):
        """
        Returns a list consisting of values at json_path on Individuals that are members of this Collective.

        :param json_path:
        :return:
        """
        pass

    @property
    def content(self):
        """
        Returns the content of the members of this Collective

        :return: a list of properties from Individual members
        """
        return [ind.content for ind in self.individual_set.all()]  # TODO: fix QuerySet caching


class Community(models.Model):
    """
    NB: When fetching a community it is recommended to prefetch Individuals, Collectives and Growths with it
    TODO: Create a SpiritField or SpiritPhase class which manages a spirit phase
    """
    default_configuration = {
        "depth": 0
    }

    enlightened = models.BooleanField(default=False)
    data = JSONField(null=True, blank=True)

    path = models.CharField(max_length=255, db_index=True)
    config = JSONField(db_index=True)  # TODO: should become a ConfigurationField

    def get_collective_from_path(self, path):
        """
        Parse a path and return the collective that belongs to that path.
        If a JSON path is specified after the hash, it will return a list of values present at that path.

        :param path:
        :return:
        """
        pass

    def grow(self):
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

    class Meta:
        abstract = True
        unique_together = ('path', 'config')


class Growth(models.Model):
    community = models.ForeignKey(Community)

    name = models.CharField(max_length=255)
    schema = JSONField()
    config = JSONField()  # TODO: should become a ConfigurationField
    process = models.CharField(max_length=255)  # TODO: set choices
    input = models.CharField(max_length=255)  # TODO: set choices
    output = models.CharField(max_length=255)  # TODO: set choices

    task_id = models.CharField(max_length=255, null=True, blank=True)


    @classmethod  # TODO: write manager instead!
    def create_from_spirit_phase(cls, spirit_phase):
        """
        Creates a new Growth instance from a Community's spirit phase.
        TODO: raise custom error when objects.create fails

        :return:
        """
        pass

    def begin(self, *args):
        """
        Starts the Celery tasks according to model fields and external arguments to enable growth.

        :param args: (optional)
        :return:
        """
        pass

    def end(self):
        """
        Takes results from self.results and creates an Organism according to ContentType stored in self.output.
        It stores a reference to the new Organism in self.output and returns it

        :return: Organism
        """
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


class ImageTranslations(Community):
    spirit = OrderedDict([
        ("translation", {
            "schema": {},
            "config": {
                "_link": "WikiTranslate"
            },
            "process": "Retrieve",
            "input": "Individual",
            "output": "Collective"
        }),
        ("visualization", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "Collective",
            "output": "Collective"
        })
    ])

    @property
    def kernel(self):
        """


        :return: spirit that is the base for results
        """
        return "translation"

    def before_translation(self, growth):
        """
        Use self.path to set initial input

        :param growth:
        :return:
        """

    def after_visualization(self, growth, output):
        """
        Add visualizations to all translations

        :param growth:
        :param output:
        :return:
        """
        pass


class PeopleSuggestions(Community):
    spirit = OrderedDict([
        ("person", {
            "schema": {},
            "config": {
                "_link": "WikiSearch"
            },
            "process": "Retrieve",
            "input": None,
            "output": "Individual"
        }),
        ("categories", {
            "schema": {},
            "config": {
                "_link": "WikiCategories"
            },
            "process": "Retrieve",
            "input": "/ind/1/#$.title",
            "output": "Collective"
        }),
        ("members", {
            "schema": {},
            "config": {
                "_link": "WikiCategoryMembers"
            },
            "process": "Retrieve",
            "input": "/col/1/#$.title",
            "output": "Collective"
        })
    ])


class CityCelebrities(Community):
    spirit = OrderedDict([
        ("radius", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": None,
            "output": "Collective"
        }),
        ("backlinks", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/col/1/#$.title",
            "output": "Collective"
        }),
        ("people_filter", {
            "schema": {},
            "config": {},
            "process": "Submit",
            "input": "/col/2/#$.wikidata",
            "output": "Collective"
        }),
        ("people_text", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/col/3/#$.title",
            "output": "Collective"
        }),
        ("location_text", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/col/1/",
            "output": "Collective"
        })
    ])


class PersonProfile(Community):
    spirit = OrderedDict([
        ("profile", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": None,
            "output": "Individual"
        }),
        ("basics", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Individual"
        }),
        ("friends", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Collective"
        }),
        ("likes", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Collective"
        }),
        ("photos", {
            "schema": {},
            "config": {},
            "process": "Retrieve",
            "input": "/ind/1/#$.fbid",
            "output": "Collective"
        })
    ])


class FamousFlightDeaths(Community):
    pass


class DataScopeView(object):
    """
    TODO: allow filtering based on GET parameters prefixed with $
    TODO: allow partial responses by respecting json paths after # in the URL
    """

    @staticmethod
    def get_user_from_request(request):
        """

        :param request:
        :return:
        """
        pass


class CommunityView(DataScopeView):

    @staticmethod
    def get_community_from_request(request):
        """

        :param request:
        :return: a Community ContentModel
        """
        pass


class CollectiveView(DataScopeView):
    pass


class IndividualView(DataScopeView):
    pass


class TextStorage(object):
    """
    Store the headers and body for any internet text source.
    """
    pass


class HttpResource(object):  # HttpLink
    """
    A representation of how to retrieve/submit data from/to a HTTP resource.
    """
    pass


class HttpRetrieve(object):
    """
    Retrieves a single http resource from the web and stores it as HyperText. Possibly returns a cached result.
    """
    pass


class HttpRetrieveMass(object):
    """
    Retrieves multiple http resources at the same time.
    """
    pass


class HttpSubmit(object):
    """
    Submits data to a http resource.
    """
    pass


class HttpSubmitBatch(object):
    """
    Submits data in small chunks to a http resource.
    """
    pass

