import pickle

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import jsonfield

from HIF.helpers.mixins import ConfigMixin
from HIF.helpers.storage import Content, ProcessContent
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
    type = models.CharField(max_length=256, blank=True)
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
        self.retained = True
        self.save()
        return (self.__class__, self.id)


    def release(self):
        self.retained = False
        self.save()
        return self.id


    def __unicode__(self):
        return self.identifier + ' | ' + self.type


    def save(self, *args, **kwargs):
        if not self.type: # this shouldn't change in Admin
            self.type = self.__class__.__name__
        self.identifier = self.identity()
        super(Storage, self).save(*args, **kwargs)


    class Meta:
        abstract = True
        unique_together = ('identifier','type',)




class ConfigStorage(ConfigMixin, Storage):

    configuration = models.TextField(null=True, blank=True)
    arguments = jsonfield.JSONField(default=tuple(), blank=True)

    # HIF vars
    HIF_namespace = "HIF"
    HIF_private = []


    def identity(self):
        return "{} | {}".format(self.arguments, self.config.dict(protected=True))


    def save(self, *args, **kwargs):
        self.configuration = pickle.dumps(self.config.dict(protected=True, private=True))
        super(Storage, self).save(*args, **kwargs)


    def load(self, fetch=True, *args, **kwargs):
        if fetch:
            super(ConfigStorage, self).load(*args,**kwargs)
        self.config(pickle.loads(self.configuration))
        return self


    class Meta:
        abstract = True




class ProcessStorage(ConfigStorage):
    """
    ..............
    """
    exception = models.TextField()
    traceback = models.TextField()
    task_id = models.CharField(max_length=256)
    processes = models.TextField(null=True, blank=True)
    prcs = ProcessContent()
    texts = models.TextField(null=True, blank=True)
    txts = Content()
    subscribers = models.TextField(null=True, blank=True)
    subs = []
    results = jsonfield.JSONField(null=True, blank=True)
    rsl = None


    def retain(self):
        print "Self: {}".format(self.serialize())
        self.prcs.retain()
        self.txts.retain()
        return super(ProcessStorage, self).retain()


    def release(self):
        self.prcs.release()
        self.txts.release()
        return super(ProcessStorage, self).release()


    def save(self, *args, **kwargs):
        self.processes = pickle.dumps(self.prcs.dict())
        self.texts = pickle.dumps(self.txts.dict())
        self.subscribers = pickle.dumps(self.subs)
        super(ProcessStorage, self).save(*args, **kwargs)


    def load(self, *args, **kwargs):
        super(ProcessStorage, self).load(*args,**kwargs)
        self.prcs(pickle.loads(self.processes))
        self.txts(pickle.loads(self.texts))
        self.subs = pickle.loads(self.subscribers)
        return self


    class Meta:
        db_table = "HIF_processstorage"
        app_label = "HIF"
        verbose_name = "Process"
        verbose_name_plural = "Processes"




class TextStorage(ConfigStorage):
    """
    Hyper text consists of a head and a body section typically
    This model adds those fields to the database
    .......
    """
    head = models.TextField()
    body = models.TextField()

    processes = models.TextField(null=True, blank=True)
    prcs = Content()

    def retain(self):
        self.prcs.retain()
        self.save()
        return super(TextStorage, self).retain()


    def release(self):
        self.prcs.release()
        return super(TextStorage, self).release()


    def save(self, *args, **kwargs):
        self.processes = pickle.dumps(self.prcs.dict())
        super(Storage, self).save(*args, **kwargs)


    def load(self, *args, **kwargs):
        super(ConfigStorage, self).load(*args,**kwargs)
        self.prcs(pickle.loads(self.processes))
        return self


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