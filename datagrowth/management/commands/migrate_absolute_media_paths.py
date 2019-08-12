import logging

from django.conf import settings
from django.core.management.base import LabelCommand
from django.apps import apps

from datagrowth.resources import HttpFileResource
from datagrowth.utils import ibatch


log = logging.getLogger("datagrowth.command")


class Command(LabelCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('-p', '--path', type=str, default=settings.MEDIA_ROOT)

    def handle(self, *labels, **options):
        log.info("Going to strip {} from paths".format(options["path"]))
        super().handle(*labels, **options)

    def handle_label(self, label, **options):
        try:
            Model = apps.get_model(label)
        except LookupError as exc:
            log.error("Failed to find '{}': {}".format(label, exc))
            return
        assert issubclass(Model, HttpFileResource)
        log.info("Stripping from {}\r".format(Model.__name__))

        batch_size = 500
        queryset = Model.objects.filter(status=200)
        count = queryset.count()
        for batch in ibatch(queryset.iterator(), batch_size, progress_bar=True, total=count):
            for instance in batch:
                if instance.body and instance.body.startswith(options["path"]):
                    instance.body = instance.body.replace(options["path"], "", 1)
                    instance.save()
