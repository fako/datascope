from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import jsonfield

from HIF.helpers import storage
from HIF.helpers.configuration import Config
from HIF.exceptions import HIFCouldNotLoadFromStorage


class Storage(models.Model):
    """
    This is an abstract base class meant to standardize storage in the Hyper Information Framework.

    Each stored entity will have an identifier for retrieval
    A type indicating the class used to do the storing
    And a status indicating the state of the data when it got stored
    identifier and type are unique together to allow different classes to use the same identifier for their storage
    Apart from these fields their are a few flags on this model
    retained indicates whether the storage happened in the context of a process which needs the content
    cached indicates whether the storage happened for performance reasons
    On top of that we have the exception and traceback fields which will get filled when errors occur

    Last but not least we have three different jsonfields which are used to save storage state
    Configuration stores the configuration arguments given to setup()
    Arguments saves the positional arguments given to setup()
    Substorage holds serialized storage objects for later use.
    """

    # Standard database fields

    identification = models.CharField(max_length=1024)  # used to find storage in db, 1 Kb to allow long unicode's
    type = models.CharField(max_length=256)  # storage is a container table of different types
    status = models.IntegerField(default=0)  # error or success code, 0 is always an initial state
    retained = models.NullBooleanField()  # to prevent huge amount of rows we collect garbage

    # Errors

    exception = models.TextField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)

    # JSON storage

    configuration = jsonfield.JSONField(null=True, blank=True, default=None)
    arguments = jsonfield.JSONField(null=True, blank=True, default=None)
    substorage = jsonfield.JSONField(null=True, blank=True, default=None)

    # HIF vars

    HIF_namespace = "HIF"
    HIF_private = []

    #######################################################
    # PYTHON + DJANGO OVERRIDES
    #######################################################

    def __init__(self, *args, **kwargs):
        """
        This function sets three key variables on self to None
        1) config will become a Config class instance holding configuration variables
        2) args will become a list of input
        3) subs will become a Container class instance holding related Storage instances
        """
        super(Storage, self).__init__(*args, **kwargs)
        self.config = None
        self.args = None
        self.subs = None

    def __unicode__(self):
        return self.identification + ' | ' + self.type

    class Meta:
        abstract = True

    #######################################################
    # GENERAL USE METHODS
    #######################################################
    # These methods are very simple functions
    # Used by Python or Django overrides and the normal class methods

    def identifier(self):
        """
        Returns an identifier based on input (args) and configuration if possible or the pk.
        Any private configuration does not count for the identity
        """
        if self.args is not None and self.config is not None:
            return "{} | {}".format(self.args, self.config.dict(protected=True))
        else:
            return str(self.id) if self.id else "0"

    def serialize(self):
        """
        Returns a tuple with information to recreate the stored object
        """
        self.save()
        return self.type, self.id

    #######################################################
    # STORAGE MAIN
    #######################################################
    # These methods are the core functionality of this class

    def load(self, serialization=None):
        """
        This method tries to load a stored version of self
        It either tries to deserialize a model
        or checks whether a model with same type and identification exists in db
        If it finds anything it loads all db fields onto self
        """
        try:
            if serialization:
                name, id = storage.deserialize(serialization)
                model = storage.get_hif_model(name)
                instance = model.objects.get(id=id)
            else:
                model = self.__class__
                instance = model.objects.get(identification=self.identification,type=self.type)
        except ObjectDoesNotExist:
            if serialization:
                message = "{} with id={} does not exist"
                raise HIFCouldNotLoadFromStorage(message.format(model, id))
            else:
                message = "{} with identifier={} and type={} does not exist"
                raise HIFCouldNotLoadFromStorage(message.format(model, self.identification, self.type))

        # Copy fields
        for field in instance._meta.fields:
            if hasattr(self,field.name):
                setattr(self,field.name, getattr(instance,field.name))

        # Enable chaining
        return self

    def setup(self, *args, **kwargs):
        """
        This function sets three key variables on self
        1) config will become a Config class instance holding configuration variables based on kwargs
        2) args will become a list of input based on args
        3) subs will become a Container class instance holding related Storage instances when needed
        """
        # Set variables based on info coming from database or this functions parameters
        identify = False
        if self.arguments is None:
            self.args = [unicode(arg) for arg in args]
            identify = True
        else:
            self.args = self.arguments
        self.config = Config(self.HIF_namespace, self.HIF_private)
        if self.configuration is None:
            self.config(kwargs)
            identify = True
        else:
            self.config(self.configuration)
        if self.substorage is None:
            self.subs = storage.Container()
        else:
            self.subs = storage.Container(self.substorage)

        # If no identification was set we try to load from db based on values now set by this function
        self.type = self.__class__.__name__
        if not self.identification:
            self.identification = self.identifier()
            identify = False
            try:
                self.load()
                self.setup(*args, **kwargs)  # we recursively will set values again based on info coming from db
            except HIFCouldNotLoadFromStorage:
                pass  # apparently current setup is new

        if identify:
            self.identification = self.identifier()

        self.save()

    #######################################################
    # PERSISTANCE
    #######################################################
    # These functions properly (de)serialize the models into db

    def retain(self, serialize=True):
        """
        Will store arguments, configuration and substorage.
        Sets retained flag to True and by default serializes the model
        This last act will save the model
        """
        self.arguments = self.args if self.args else None
        self.configuration = self.config.dict(protected=True, private=True) if self.config.dict(protected=True) else None
        self.substorage = self.subs.dict() if self.subs.dict() else None
        self.retained = True
        if serialize:
            return self.serialize()
        else:
            return True

    def release(self):
        self.retained = False
        self.save()


class ProcessStorage(Storage):
    """
    A hyper process currently stores meta information in dictionary form and results.
    It can also store a Celery task_id when storing an async process
    """

    # Results
    meta = jsonfield.JSONField(null=True, blank=True, default=None)
    results = jsonfield.JSONField(null=True, blank=True, max_length=1048576*10, default=None)  # 10Mb

    # Async processing
    task_id = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        db_table = "HIF_processstorage"
        app_label = "HIF"
        verbose_name = "Process"
        verbose_name_plural = "Processes"


class TextStorage(Storage):
    """
    Hyper text consists of a head and a body section typically
    This model adds those fields to the database
    """

    head = jsonfield.JSONField(default=None)
    body = models.TextField()

    class Meta:
        db_table = "HIF_textstorage"
        app_label = "HIF"
        verbose_name = "Text"
        verbose_name_plural = "Texts"


class FileStorage():
    """
    To be implemented with FTP or HTTP file transfer
    """
    pass