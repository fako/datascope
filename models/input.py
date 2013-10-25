from django.conf import settings
from django.db import models

from HIF.exceptions import HIFDBResponse
from HIF.models.processors import DataProcess

class DataLink(models.Model):

    # Django fields
    link = models.URLField()
    link_type = models.CharField(max_length=256)
    response = models.TextField()
    response_status = models.IntegerField() # error or success code
    hibernation = models.BooleanField(default=False)
    processes = models.ManyToManyField(DataProcess)

    # Class attributes
    auth_link = ''
    cache = False
    results = []
    db = None

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

    # Interface

    # Check whether a certain link exists in the database.
    def has_db(self, *args, **kwargs):
        if self.db:
            return self.db
        if not self.auth_link:
            self.enable_auth()
        try:
            self.db = DataLink.objects.get(link=self.auth_link)
            return self.db
        except DataLink.DoesNotExist:
            return False

    # Main function.
    # Returns a list with results coming from link
    def get(self, refresh=False, *args, **kwargs):

        try:
            # Early exit if results are already there.
            if self.results and not refresh:
                return self.results
            else:
                self.results = []

            # Get recipe
            self.prepare_link()
            self.enable_auth()
            self.send_request(*args, **kwargs)
            self.handle_error()
            self.continue_request()
            self.store_response()

            self.results = self.extract_results()
            self.results = self.translate_results()
            self.results = filter(self.cleaner,self.results)

        except HIFDBResponse:
            self.results = self.extract_results()
            self.results = self.translate_results()
            self.results = filter(self.cleaner,self.results)

            return self.results

        return self.results

    def prepare_link(self):
        pass

    def enable_auth(self):
        self.auth_link = self.link

    def send_request(self, *args, **kwargs):
        # Check whether link was already fetched
        db = self.has_db(*args, **kwargs)
        # Copy all Django fields from database to self if available
        if db:
            for field in db._meta.fields:
                if hasattr(self,field.name):
                    setattr(self,field.name,getattr(db,field.name))
            # Change flow for db result cases
            raise HIFDBResponse
        else:
            return True

    def handle_error(self):
        pass

    def continue_request(self):
        pass

    def store_response(self):
        if self.cache and self.response:
            self.save()
            return True
        return False

    def extract_results(self):
        return self.results

    def translate_results(self):
        if self._translations:
            for r in self.results:
                for k,v in self._translations.iteritems():
                    if k in r: # if a key that needs translation is found
                        r[v] = r[k] # make a new pair in result with the translated key as key
                        del(r[k]) # delete the old key/value pair
        return self.results

    def hibernate(self):
        if self.results:
            self.hibernation = True
            self.save()
            return True
        return False

    def cleaner(self,rsl):
        return True

    class Meta:
        db_table = "HIF_datalink"
        app_label = "HIF"


class DataLinkMixin(object):
    class Meta:
        proxy = True
        db_table = "HIF_datalink"
        app_label = "HIF"