from __future__ import unicode_literals, absolute_import, print_function, division
# noinspection PyUnresolvedReferences
from six.moves.urllib.parse import parse_qsl

import argparse
import time
from datetime import datetime

from django.core.management.base import BaseCommand

from core.utils.helpers import get_any_model
from core.exceptions import DSProcessUnfinished


class DecodeConfigAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        values = dict(parse_qsl(values))
        setattr(namespace, self.dest, values)


class Command(BaseCommand):
    """
    Continuously polls a Community until it's completely grown.
    """

    def add_arguments(self, parser):
        parser.add_argument('community', type=unicode)
        parser.add_argument('-a', '--args', type=unicode, nargs="*", default="")
        parser.add_argument('-c', '--config', type=unicode, action=DecodeConfigAction, nargs="?", default={})

    def handle(self, *args, **options):
        Community = get_any_model(options["community"])
        community = Community.get_or_create_by_input(*args, **options["config"])
        print("Start:", datetime.now())
        done = False
        while not done:
            try:
                done = community.grow()
                if done:
                    print("Result:", community.kernel)
                    print("Growth:", [growth.id for growth in community.growth_set.all()])
            except DSProcessUnfinished:
                time.sleep(5)
                continue
        print("End:", datetime.now())

