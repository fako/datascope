import json

from django.db import models

from HIF.exceptions import HIFDataLinkPending


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
        except HIFDataLinkPending:
            self.hibernate()
            return None