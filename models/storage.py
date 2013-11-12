import pickle

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

import jsonfield

from HIF.helpers.mixins import ConfigMixin
from HIF.exceptions import HIFCouldNotLoadFromStorage


class Storage(models.Model):
    """
    This is an abstract base class meant to standardize storage in the Hyper Information Framework.

    Each stored entity will have an identifier for retrieval
    A type indicating the class used to do the storing
    And a status indicating the state of the data when it got stored
    identifier and type are unique together to allow different classes to use the same identifier for their storage
    Apart from these fields their are a few flags on this model
    hibernating indicates whether the storage happened in the context of hibernation
    cached indicates whether the storage happened for performance reasons
    """
    identifier = models.CharField(max_length=256)
    type = models.CharField(max_length=256, blank=True)
    status = models.IntegerField(default=0) # error or success code, 0 means Status.NONE

    retained = models.NullBooleanField()
    cached = models.NullBooleanField()

    def load(self, identifier=None): # TODO: identifier= still used with new style identifiers? remove?
        """
        This function tries to load a stored version of self

        It will set type to the current class and gets the identifier from self or as an argument
        Then it will do a database get and copy all fields to self
        """
        # Set type
        self.type = self.__class__.__name__
        # Assure identifier
        if identifier is None and not self.identifier:
            raise HIFCouldNotLoadFromStorage("No storage identifier set or given")
        elif identifier is not None:
            self.identifier = identifier

        # Database lookup
        try:
            model = self.__class__.objects.get(identifier=self.identifier,type=self.type)
        except ObjectDoesNotExist:
            message = "Model with identifier={} and type={} does not exist"
            raise HIFCouldNotLoadFromStorage(message.format(self.identifier, self.type))
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
        if not self.type:
            self.type = self.__class__.__name__
        super(Storage, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        unique_together = ('identifier','type',)


class ConfigStorage(ConfigMixin, Storage):

    configuration = models.TextField()

    def identity(self, *args):
        arguments = str([str(arg) for arg in args])
        configuration = str(self.config)
        return "{} | {}".format(arguments, configuration)

    def save(self, *args, **kwargs):
        if not self.configuration:
            self.configuration = pickle.dumps(self.config.dict())
        super(Storage, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ProcessStorage(ConfigStorage):
    """
    A process stores a result and a Celery task_id
    This model adds those fields to the database
    ProcessStorage is a concrete model
    """
    task = models.CharField(max_length=256)
    processes = models.ManyToManyField("ProcessStorage", blank=True, null=True)

    results = jsonfield.JSONField(null=True, blank=True)
    args = jsonfield.JSONField(null=True, blank=True)

    # HIF vars
    HIF_namespace = "HIF"

    def retain(self, parent=None):
        # retain everything in text_set
        for text in self.text_set.all():
            text.retain()
        # retain parent as process where appropriate
        if parent:
            self.processes.add(parent)
        return super(ProcessStorage, self).retain()

    def release(self):
        for text in self.text_set.all():
            text.release()
        return super(ProcessStorage, self).release()

    class Meta:
        db_table = "HIF_processstorage"
        app_label = "HIF"
        verbose_name = "Process"
        verbose_name_plural = "Processes"


class TextStorage(ConfigStorage):
    """
    Hyper text consists of a head and a body section typically
    This model adds those fields to the database
    Text is seldom stored without the context of a process using the text
    That's why we add a relation to HIFProcessStorage
    TextStorage is a concrete model
    """
    head = models.TextField()
    body = models.TextField()

    processes = models.ManyToManyField(ProcessStorage, related_name="text_set", blank=True, null=True)

    HIF_namespace = "HIF"

    class Meta:
        db_table = "HIF_textstorage"
        app_label = "HIF"
        verbose_name = "Text"
        verbose_name_plural = "Texts"


class HttpStorage(TextStorage):
    """
    This class does nothing but allowing for its subclasses to add their methods without creating separate tables
    """
    class Meta:
        proxy = True


class EmailStorage(TextStorage):
    """
    This class does nothing but allowing for its subclasses to add their methods without creating separate tables
    """
    class Meta:
        proxy = True


class FileStorage():
    """
    To be implemented with FTP or HTTP file transfer
    """
    pass