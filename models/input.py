from django.conf import settings
from django.db import models

from HIF.exceptions import DbResponse


class DataLink(models.Model):

    # Django fields
    link = models.URLField()
    link_type = models.CharField(max_length=256)
    response = models.TextField()
    hibernation = models.BooleanField(default=False)

    # Class attributes
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
                return self.results
            else:
                self.results = []

            # Get recipe
            self.prepare_link()
            self.enable_auth()
            self.send_request()
            self.handle_error()
            self.continue_request()
            self.store_response()

            self.results = self.extract_results()
            self.results = self.translate_results()
            self.results = filter(self.cleaner,self.results)

        except DbResponse:
            self.results = self.extract_results()
            self.results = self.translate_results()
            self.results = filter(self.cleaner,self.results)

            return self.results

        return self.results

    def prepare_link(self):
        pass

    def enable_auth(self):
        self.auth_link = self.link

    def send_request(self):
        try:
            # Get link from db.
            db_link = DataLink.objects.get(link=self.auth_link)
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