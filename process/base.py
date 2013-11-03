import json

from django.db import models

from celery.result import AsyncResult


class DataProcessTemp(models.Model):

    args = models.CharField(max_length=256)
    kwargs = models.CharField(max_length=256)
    task_id = models.CharField(max_length=256)
    results = models.TextField(null=True,default='')
    hibernation = models.BooleanField()

    def hibernate(self):
        # Hibernate all DataLink objects in the datalink_set for future reference.
        for link in self.datalink_set.all():
            link.hibernate()

        # Set hibernation flag
        self.hibernation = True

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

            # Return True to indicate awakening
            return True

        except DataProcess.DoesNotExist:
            return False

    # This functions indicates Celery's process
    def ready(self, *args, **kwargs):
        if self.task_id:
            return AsyncResult(self.task_id).ready()
        else:
            return False

    # This is a function to extend
    # It starts the tasks necessary to do the processing
    def process(self):
        return False

    # This is a function to extend.
    # It should save and return the results based on task_id results
    def post_process(self, *args, **kwargs):
        return None

    def execute(self, *args, **kwargs):
        # Set arguments in model
        self.args = json.dumps(list(args))
        self.kwargs = json.dumps(dict(kwargs))

        # gets hibernating processes from the db.
        self.awake()
        if self.ready(): # processing done, store it
            self.post_process()
            return self.results
        elif not self.task_id: # processing hasn't started
            self.process()
            return True
        else: # processing busy
            return False

    class Meta:
        db_table = "HIF_dataprocess"
        app_label = "HIF"
