import json

from django.conf import settings
from django.db import models

from .exceptions import DbResponse, WaitingForAPIResponse, WarningImproperUsageLinkPool, DataProcessCompleted

# Create your models here.
class DataLink(models.Model):

    # Django fields
    link = models.URLField()
    link_type = models.CharField(max_length=256)
    response = models.TextField()
    hibernation = models.BooleanField(default=False)

    # Public attributes
    auth_link = ''
    cache = False
    results = []

    # HIF interface attributes
    _link_type = 'DataLink'
    _link = ''
    _objective = {}
    _translations = {}

    def __unicode__(self):
        return self.link + ' | ' + self.link_type

    def __init__(self, *args, **kwargs):
        super(DataLink, self).__init__(*args, **kwargs)
        # Always cache in debug mode
        if settings.DEBUG:
            self.cache = True

    def __iter__(self):
        return iter(self.results)

    # Abstract interface

    # Main function.
    # Returns an iterator with results coming from DataLink
    def get(self, refresh=False):

        try:
            # Early exit if results are already there.
            if self.results and not refresh:
                return iter(self.results)

            # Get recipe
            self.prepare_link()
            self.enable_auth()
            self.send_request()
            self.handle_error()
            self.continue_request()
            self.store_response()

            self.extract_results()
            self.translate_results()
            self.results = filter(self.cleaner,self.results)

        except DbResponse:
            self.extract_results()
            self.translate_results()
            self.results = filter(self.cleaner,self.results)

            return iter(self.results)

        return iter(self.results)

    def prepare_link(self):
        pass

    def enable_auth(self):
        self.auth_link = self.link

    def send_request(self):
        try:
            # Get link from db.
            db_link = DataLink.objects.get(link=self.link)
            # Copy all Django fields from database to self
            for field in db_link._meta.fields:
                if hasattr(self,field.name):
                    setattr(self,field.name,getattr(db_link,field.name))
            # Change flow for db result cases
            raise DbResponse
        except DataLink.DoesNotExist:
            pass

        return True

    def handle_error(self):
        pass

    def continue_request(self):
        pass

    def store_response(self):
        if self.cache and self.response:
            self.save()

    def extract_results(self):
        pass

    def translate_results(self):
        if self._translations:
            for r in self.results:
                for k,v in self._translations.iteritems():
                    if k in r: # if a key that needs translation is found
                        r[v] = r[k] # make a new pair in result with the translated key as key
                        del(r[k]) # delete the old key/value pair

    def hibernate(self):
        if self.results:
            self.hibernation = True
            self.save()

    def cleaner(self,rsl):
        return True


class DataLinkMixin(object):
    class Meta:
        proxy = True


class DataProcess(models.Model):

    args = models.CharField(max_length=256)
    kwargs = models.CharField(max_length=256)
    initial_storage = models.TextField()
    results = models.TextField(null=True,default='')
    ready = models.BooleanField(default=False)

    link_pool = []
    initial = None

    def hibernate(self):
        # Store initial calculations if they are there
        if self.initial:
            self.initial_storage = json.dumps(self.initial)

        # Hibernate all DataLink objects in the link_pool for future reference.
        if self.link_pool:
            for link in self.link_pool:
                link.hibernate()

        # Save self to database for later resurrection
        self.save()

    def awake(self):
        try:
            # Get process from db based on arguments given to execute.
            db_process = DataProcess.objects.get(args=self.args,kwargs=self.kwargs)

            # Copy all Django fields from database to self
            for field in db_process._meta.fields:
                if hasattr(self,field.name):
                    setattr(self,field.name,getattr(db_process,field.name))

            # Set initial values if they are there
            if self.initial_storage:
                self.initial = json.loads(self.initial_storage)

            # Return True to indicate awakening
            return True

        except DataProcess.DoesNotExist:
            return False

    # This is a function to extend.
    # It should set self.initial to a value that makes sense for the process to work with.
    def initialize(self, *args, **kwargs):
        return None

    # This is a function to extend.
    # It should return the results or None when they are not there yet.
    # It should make use of self.initial for getting the initial data to work on.
    def process(self, *args, **kwargs):
        return None

    def execute(self, *args, **kwargs):
        # Set arguments in model
        self.args = json.dumps(list(args))
        self.kwargs = json.dumps(dict(kwargs))
        try:
            self.awake() # gets hibernating processes from the db.
            if self.ready:
                return self.results
            else:
                if not self.initial: self.initialize(*args,**kwargs)
                self.results = self.process()
                if self.results is not None:
                    self.ready = True
                    self.save()
                return self.results
        except WaitingForAPIResponse:
            self.hibernate()
            return None