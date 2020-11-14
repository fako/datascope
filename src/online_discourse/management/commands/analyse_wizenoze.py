from operator import itemgetter
from pprint import pprint
import logging

import numpy as np

from django.core.management.base import BaseCommand

from core.models import Collective


log = logging.getLogger("datascope")


class Command(BaseCommand):
    """
    Base command for Community centered commands
    """

    def add_arguments(self, parser):
        return

    def handle(self, *args, **options):
        collective = Collective.objects.get(id=11577)
        reading_levels = {}
        level_probability_diffs = {}
        missing_audience = 0
        missing_probabilities = 0
        for individual in collective.individual_set.all():
            if "audience" not in individual.properties:
                missing_audience += 1
                continue
            if individual["audience_probabilities"] is None:
                missing_probabilities += 1
                continue
            audience = individual["audience"]
            if audience["level"] < 4 and "argument_score" in individual.properties:
                print(audience["level"], individual["argument_score"], individual["url"])
            audience_propabilities = {
                individual["audience"]["level"]: individual["probability"]
                for individual in individual["audience_probabilities"]
            }
            level_probabilities = dict(sorted(audience_propabilities.items(), key=itemgetter(0), reverse=True))
            if audience["label"] not in reading_levels:
                reading_levels[audience["label"]] = 1
            else:
                reading_levels[audience["label"]] += 1
            for level, probability in level_probabilities.items():
                if level == 1:
                    continue
                if level not in level_probability_diffs:
                    level_probability_diffs[level] = [level_probabilities[level-1]]
                else:
                    level_probability_diffs[level].append(level_probabilities[level-1])
        for level, diff in level_probability_diffs.items():
            level_probability_diffs[level] = np.mean(diff)
        print("Missing audience is {} and missing probabilities is {}, while total is {}".format(
            missing_audience, missing_probabilities, collective.individual_set.count()))
        pprint(reading_levels)
        pprint(level_probability_diffs)