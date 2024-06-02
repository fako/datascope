import logging

from datagrowth.management.commands.grow_dataset import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction

from online_discourse.discourse import configurations


log = logging.getLogger("datascope")


class Command(GrowCommand):

    cast_as_community = True
    dataset_model = "online_discourse.DiscourseSearchCommunity"

    def add_arguments(self, parser):
        parser.add_argument('topic', type=str)
        parser.add_argument('--dataset', type=str, nargs="?", default=self.dataset_model)
        parser.add_argument('-c', '--config', type=str, action=DecodeConfigAction, nargs="?", default={})

    def handle(self, *args, **kwargs):
        topic = kwargs.pop("topic")
        try:
            configuration = getattr(configurations, topic)
        except AttributeError:
            log.error('Can not find configuration for topic "{}"'.format(topic))
            return
        args += (topic,)
        kwargs["config"]["language"] = configuration.language
        super().handle(*args, **kwargs)
