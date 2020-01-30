import logging

from datagrowth.management.commands.grow_dataset import Command as GrowCommand
from core.utils.configuration import DecodeConfigAction

from online_discourse.discourse import configurations


log = logging.getLogger("datascope")


class Command(GrowCommand):

    community_model = "DiscourseSearchCommunity"

    def add_arguments(self, parser):
        parser.add_argument('topic', type=str)
        parser.add_argument('--community', type=str, nargs="?", default=self.community_model)
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
