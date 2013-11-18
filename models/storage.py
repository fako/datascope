import pickle

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import jsonfield

from HIF.helpers.mixins import ConfigMixin
from HIF.helpers.storage import ContentMixin
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
    """
    identifier = models.CharField(max_length=256)
    type = models.CharField(max_length=256)
    status = models.IntegerField(default=0) # error or success code, 0 is always an initial state

    retained = models.NullBooleanField()
    cached = models.NullBooleanField()


    def identity(self):
        return str(self.id)


    def serialize(self):
        return (self.__class__, self.id)


    def load(self, id=0):
        """
        This function tries to load a stored version of self

        It will set type to the current class and gets the identifier from self or as an argument
        Then it will do a database get and copy all fields to self
        """

        # Set type
        self.type = self.__class__.__name__
        # Assure identifier
        self.identifier = self.identity()

        # Database lookup
        try:
            if not id:
                model = self.__class__.objects.get(identifier=self.identifier,type=self.type)
            else:
                model = self.__class__.objects.get(id=id)
        except ObjectDoesNotExist:
            if not id:
                message = "Model with identifier={} and type={} does not exist"
                raise HIFCouldNotLoadFromStorage(message.format(self.identifier, self.type))
            else:
                message = "Model with id={} does not exist"
                raise HIFCouldNotLoadFromStorage(message.format(id))

        # Copy fields
        for field in model._meta.fields:
            if hasattr(self,field.name):
                setattr(self,field.name, getattr(model,field.name))

        # Enable chaining
        return self


    def retain(self):
        """
        Retain is the save function for HIF models, which returns a retain tuple.
        It manages the classes that get added as attributes in Storage subclasses
        At this level we just indicate that the object is being retained,
        we set the properties needed to load it later
        and we call Django's save to store.

        The returned tuple is meant as an indicator to which load function should get called
        """
        self.type = self.__class__.__name__
        self.identifier = self.identity()
        self.retained = True

        self.save()
        return (self.__class__, self.id)


    def release(self):
        self.retained = False
        self.save()
        return self.id


    def __unicode__(self):
        return self.identifier + ' | ' + self.type


    class Meta:
        abstract = True
        unique_together = ('identifier','type',)




class ConfigStorage(ConfigMixin, Storage):

    configuration = models.TextField(null=True, blank=True)
    arguments = jsonfield.JSONField(default=list(), blank=True)

    # HIF vars
    HIF_namespace = "HIF"
    HIF_private = []


    def identity(self):
        return "{} | {}".format(self.arguments, self.config.dict(protected=True))


    def retain(self):
        """
        On retain we dump the complete config in a pickle field
        """
        self.configuration = pickle.dumps(self.config.dict(protected=True, private=True))
        return super(ConfigStorage, self).retain()


    def load(self, fetch=True, *args, **kwargs):
        print "Load call with fetch={}".format(fetch)
        if fetch: # TODO: needed?
            super(ConfigStorage, self).load(*args,**kwargs)
        self.config(pickle.loads(self.configuration))
        return self


    class Meta:
        abstract = True




class ContentStorage(ContentMixin, ConfigStorage):

    # Content
    processes = models.TextField(null=True, blank=True)
    texts = models.TextField(null=True, blank=True)


    def retain(self):
        # Manage content
        self.prcs.retain()
        self.txts.retain()
        # Save classes in fields
        self.processes = pickle.dumps(self.prcs.dict())
        self.texts = pickle.dumps(self.txts.dict())
        return super(ContentStorage, self).retain()


    def release(self):
        self.prcs.release()
        self.txts.release()
        return super(ContentStorage, self).release()


    def load(self, *args, **kwargs):
        super(ContentStorage, self).load(*args,**kwargs)
        self.prcs(pickle.loads(self.processes))
        self.txts(pickle.loads(self.texts))
        return self


    class Meta:
        abstract = True




class ProcessStorage(ContentStorage):
    """
    ..............
    """

    results = jsonfield.JSONField(null=True, blank=True)

    # Errors
    exception = models.TextField()
    traceback = models.TextField()

    # Async processing
    task_id = models.CharField(max_length=256)
    subscribers = models.TextField(null=True, blank=True)
    subs = []


    def retain(self):
        self.subscribers = pickle.dumps(self.subs)
        return super(ProcessStorage, self).retain()


    def load(self, *args, **kwargs):
        super(ProcessStorage, self).load(*args,**kwargs)
        self.subs = pickle.loads(self.subscribers)
        return self


    class Meta:
        db_table = "HIF_processstorage"
        app_label = "HIF"
        verbose_name = "Process"
        verbose_name_plural = "Processes"




class TextStorage(ContentStorage):
    """
    Hyper text consists of a head and a body section typically
    This model adds those fields to the database
    .......
    """
    head = models.TextField()
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