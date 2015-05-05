from django.db import models

import jsonfield

from .community import Community


class Growth(models.Model):

    success_codes = [200, 201, 202, 204]

    community = models.ForeignKey(Community)

    name = models.CharField(max_length=255)
    schema = jsonfield.JSONField()
    config = jsonfield.JSONField()  # TODO: should become a ConfigurationField
    process = models.CharField(max_length=255)  # TODO: set choices
    input = models.CharField(max_length=255)  # TODO: set choices
    output = models.CharField(max_length=255)  # TODO: set choices

    task_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255)  # TODO: set choices


    @classmethod  # TODO: write manager instead!
    def create_from_spirit_phase(cls, spirit_phase):
        """
        Creates a new Growth instance from a Community's spirit phase.
        TODO: raise custom error when objects.create fails

        :return:
        """
        pass

    def begin(self, *args):
        """
        Starts the Celery tasks according to model fields and external arguments to enable growth.

        :param args: (optional)
        :return: the input Organism
        """
        pass

    def end(self):
        """
        Takes results from self.results and creates an Organism according to ContentType stored in self.output.
        It stores a reference to the new Organism in self.output and returns it.
        Will ignore any errors that are not specified in self.errors and

        :return: the output Organism
        """
        pass

    def create_processor(self, *args, **kwargs):
        """
        Creates an instance of process based on self.process, self.config and args

        :param args:
        :param kwargs: (optional)
        :return:
        """
        pass

    @property
    def progress(self):
        """
        Tries to load the task_id as AsyncResult or GroupResult and indicates task progress.

        :return:
        """
        return None

    @property
    def results(self):  # TODO: make this class iterable
        """
        Returns a Storage class and all ids that were created for the growth

        :return:
        """
        return None