import logging

from datagrowth.management.base import DatasetCommand


log = logging.getLogger("datagrowth.command")


class Command(DatasetCommand):
    """
    Grows a Dataset synchronously
    """

    def get_datasets(self):
        raise TypeError("It is impossible to grow multiple datasets at the same time.")

    def handle_community(self, dataset, *args, **options):
        dataset.config = {"async": False}  # TODO: this is weird syntax as it is actually performing an update
        dataset.save()
        dataset.grow(*args)
        log.info("Result: {}".format(dataset.kernel))
        log.info("Growth: {}".format([growth.id for growth in dataset.growth_set.all()]))
