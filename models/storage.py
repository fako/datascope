from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.loading import get_model

import jsonfield

from HIF.helpers.subclasses import Config, Container, deserialize
from HIF.exceptions import HIFImproperUsage, HIFCouldNotLoadFromStorage




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

    # Standard database fields

    identification = models.CharField(max_length=256)  # used to find storage in db
    type = models.CharField(max_length=256)  # storage is a container table of different types
    status = models.IntegerField(default=0)  # error or success code, 0 is always an initial state
    retained = models.NullBooleanField()  # to prevent huge amount of rows we collect garbage

    # Errors

    exception = models.TextField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)

    # JSON storage

    configuration = jsonfield.JSONField(null=True, blank=True)
    arguments = jsonfield.JSONField(null=True, blank=True)
    substorage = jsonfield.JSONField(null=True, blank=True)

    # HIF vars

    HIF_namespace = "HIF"
    HIF_private = []


    def __init__(self, *args, **kwargs):
        super(Storage, self).__init__(*args, **kwargs)
        self.config = None
        self.args = None
        self.subs = None

    def __unicode__(self):
        return self.identification + ' | ' + self.type

    class Meta:
        abstract = True


    def identifier(self):
        if self.args is not None and self.config is not None:
            return "{} | {}".format(self.args, self.config.dict(protected=True))
        else:
            return str(self.id) if self.id else "0"

    def serialize(self):
        self.save()
        return self.type, self.id


    def load(self, serialization=None):
        """
        This function tries to load a stored version of self
        It either tries to deserialize a model
        or checks whether a model with same type and identification exists in db
        """
        try:
            if serialization:
                typ, id = deserialize(serialization)
                model = get_model(app_label="HIF", model_name=typ)
                if model is None:
                    raise HIFImproperUsage("The specified model does not exist or is not registered as Django model with HIF label.")
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

        """
        print "Setting up {} with {} and {}".format(self.__class__.__name__, args, kwargs)
        identify = False
        if self.arguments is None:
            self.args = list(args)
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
            self.subs = Container()
        else:
            self.subs = Container(self.substorage)

        self.type = self.__class__.__name__
        if not self.identification:
            self.identification = self.identifier()
            identify = False
            try:
                self.load()
                self.setup(*args, **kwargs)
            except HIFCouldNotLoadFromStorage:
                pass

        if identify:
            self.identification = self.identifier()

        self.save()


    def retain(self, serialize=True):
        self.arguments = self.args if self.args else None
        self.configuration = self.config.dict(protected=True, private=True) if self.config.dict(protected=True) else None
        self.substorage = self.subs.dict() if self.subs.dict() else None
        print "Retaining with: {}, {} and {}".format(self.arguments, self.configuration, self.substorage)
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
    ..............
    """

    # Results
    meta = jsonfield.JSONField(null=True, blank=True)
    results = jsonfield.JSONField(null=True, blank=True)

    # Async processing
    task_id = models.CharField(max_length=256, null=True, blank=True)
    listeners = jsonfield.JSONField(null=True, blank=True)
    #subscribers = PickledObjectField(null=True, blank=True)
    #subs = []


    #def __init__(self, *args, **kwargs):
    #    super(ProcessStorage, self).__init__(*args, **kwargs)
    #    self._results = None
    #
    #
    #def retain(self):
    #    self.subscribers = pickle.dumps(self.subs)
    #    if self.results:
    #        self.results = json.dumps(self._results)
    #    #self.subscribers = self.subs
    #    return super(ProcessStorage, self).retain()
    #
    #
    #def load(self, *args, **kwargs):
    #    super(ProcessStorage, self).load(*args,**kwargs)
    #    #self.subs = pickle.loads(self.subscribers)
    #    print "Load results: ".format(self.results)
    #    if self.results:
    #        self._results = json.loads(self.results)
    #    else:
    #        self._results = []
    #    #self.subs = self.subscribers
    #    return self


    class Meta:
        db_table = "HIF_processstorage"
        app_label = "HIF"
        verbose_name = "Process"
        verbose_name_plural = "Processes"




class TextStorage(Storage):
    """
    Hyper text consists of a head and a body section typically
    This model adds those fields to the database
    .......
    """

    head = jsonfield.JSONField()
    body = models.TextField()

    class Meta:
        db_table = "HIF_textstorage"
        app_label = "HIF"
        verbose_name = "Text"
        verbose_name_plural = "Texts"





#    def retain(self):
#        # Manage content
#        self.prcs.retain()
#        self.txts.retain()
#        # Save classes in fields
#        self.processes = pickle.dumps(self.prcs.dict())
#        self.texts = pickle.dumps(self.txts.dict())
#        return super(ContentStorage, self).retain()
#
#
#    def release(self):
#        self.prcs.release()
#        self.txts.release()
#        return super(ContentStorage, self).release()
#
#
#    def load(self, *args, **kwargs):
#        super(ContentStorage, self).load(*args,**kwargs)
#        self.prcs(pickle.loads(self.processes))
#        self.txts(pickle.loads(self.texts))
#        return self
#
#
#    class Meta:
#        abstract = True
#
#
#
#
#
#
#
#
#    def setup(self, *args, **kwargs):
#        """
#
#        """
#        assert isinstance(config,dict), "Setup is expecting to get a dictionary as argument."
#        for key,value in config.iteritems():
#            setattr(self.config,key,value)
#        self.identification = self.identifier()
#
#
#
#
#
#    def retain(self):
#        """
#        On retain we dump the complete config in a pickle field
#        """
#        self.configuration = pickle.dumps(self.config.dict(protected=True, private=True))
#        self.arguments = json.dumps(self.args)
#        return super(ConfigStorage, self).retain()
#
#
#    def load(self, fetch=True, *args, **kwargs):
#        print "Load call with fetch={}".format(fetch)
#        if fetch:
#            super(ConfigStorage, self).load(*args,**kwargs)
#        self.config(pickle.loads(self.configuration))
#        if self.arguments:
#            print "Args on load: {}".format(self.arguments)
#            self.args = json.loads(self.arguments)
#        else:
#            self.args = []
#        return self
#
#
#    class Meta:
#        abstract = True
#
#
#    def __init__(self, *args, **kwargs):
#        super(Storage, self).__init__(*args, **kwargs)
#
#        self.identification = self.identifier()
#
#
#
#
#
#
#    def identifier(self):
#
#
#
#
#
#
#    def retain(self):
#        """
#        Retain is the save function for HIF models, which returns a retain tuple.
#        It manages the classes that get added as attributes in Storage subclasses
#        At this level we just indicate that the object is being retained,
#        we set the properties needed to load it later
#        and we call Django's save to store.
#
#        The returned tuple is meant as an indicator to which load function should get called
#        """
#        self.identification = self.identifier()
#        self.retained = True
#
#        self.save()
#        content_type = ContentType.objects.get_for_model(self)
#        return (self.type, content_type.id, self.id)
#
#
#    def release(self):
#        self.retained = False
#        self.save()
#        return self.id
#
#
#
#
#
#    class Meta:
#        abstract = True
#        unique_together = ('identification','type',)
#
#
#
#
#
#

#
#
#
#
#class FileStorage():
#    """
#    To be implemented with FTP or HTTP file transfer
#    """
#    pass