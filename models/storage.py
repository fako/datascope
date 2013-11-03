from django.db import models
from django.core.exceptions import ObjectDoesNotExist

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
    type = models.CharField(max_length=256)
    status = models.IntegerField(default=0) # error or success code

    hibernating = models.NullBooleanField()
    cached = models.NullBooleanField()

    def load(self, identifier=None):
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
            raise HIFCouldNotLoadFromStorage("Model with identifier={} and type={} does not exist".format(self.identifier, self.type))
        # Copy fields
        for field in model._meta.fields:
            if hasattr(self,field.name):
                setattr(self,field.name, getattr(model,field.name))
        # Enable chaining
        return self

    def hibernate(self):
        self.hibernating = True
        self.save()
        return self

    def __unicode__(self):
        return self.identifier + ' | ' + self.type

    def save(self, *args, **kwargs):
        self.type = self.__class__.__name__
        super(Storage, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        unique_together = ('identifier','type',)


class ProcessStorage(Storage):
    """
    A process stores a result and a Celery task_id
    This model adds those fields to the database
    ProcessStorage is a concrete model
    """
    results = models.TextField()
    task = models.CharField(max_length=256)
    processes = models.ManyToManyField("ProcessStorage")

    class Meta:
        db_table = "HIF_processstorage"
        app_label = "HIF"
        verbose_name = "Process"
        verbose_name_plural = "Processes"


class TextStorage(Storage):
    """
    Hyper text consists of a head and a body section typically
    This model adds those fields to the database
    Text is seldom stored without the context of a process using the text
    That's why we add a relation to HIFProcessStorage
    TextStorage is a concrete model
    """
    head = models.TextField()
    body = models.TextField()

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