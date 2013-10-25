import json

from django.db import models


class DataProcess(models.Model):

    args = models.CharField(max_length=256)
    kwargs = models.CharField(max_length=256)
    initial_storage = models.TextField()
    results = models.TextField(null=True,default='')
    ready = models.BooleanField(default=False)

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
    # It should start Celery to fetch all data
    # Returns True when all data is there or False when it isn't
    def fetch(self, *args, **kwargs):
        return False

    # This is a function to extend.
    # It should return the results from processing
    # It assumes fetch has gathered all data
    def process(self, *args, **kwargs):
        return None

    def execute(self, *args, **kwargs):
        # Set arguments in model
        self.args = json.dumps(list(args))
        self.kwargs = json.dumps(dict(kwargs))

        # gets hibernating processes from the db.
        self.awake()
        # return when we have results already
        if self.results:
            return self.results
        # start with initial if it is not there
        if not self.initial:
            self.initialize(*args,**kwargs)
        # fetch data
        if self.fetch():
            # process data if it is there
            self.ready = True
            self.results = self.process()
            self.save()
            return self.results
        else:
            # hibernate as long as data is incomplete
            self.hibernate()
            return None

    class Meta:
        db_table = "HIF_dataprocess"
        app_label = "HIF"