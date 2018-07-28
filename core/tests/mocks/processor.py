from core.utils.configuration import ConfigurationProperty
from datascope.configuration import MOCK_CONFIGURATION
from core.processors.base import Processor
from core.processors import RankProcessor


class MockProcessor(Processor):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=MOCK_CONFIGURATION,
        namespace="mock_processor",
        private=[]
    )


class MockNumberProcessor(MockProcessor):

    def number_individuals(self, individuals):
        def number_individual(individual, number):
            individual["number"] = number
            return individual
        return (number_individual(individual, idx+1) for idx, individual in enumerate(individuals))


class MockFilterProcessor(MockProcessor):

    def filter_individuals(self, individuals):
        for individual in individuals:
            if self.config.include_odd and individual.get("number") % 2:
                yield individual
            elif self.config.include_even and not individual.get("number") % 2:
                yield individual
            elif self.config.include_odd and self.config.include_even:
                yield individual


class MockRankProcessor(RankProcessor):

    @staticmethod
    def rank_by_value(individual):
        return individual["value"]

    @staticmethod
    def is_double(individual):
        return 1 if "double" in individual["name"] else 0

    @staticmethod
    def is_highest(individual):
        return 1 if "highest" in individual["name"] else 0

    @staticmethod
    def ban_highest(individual):
        return 0.5 if "highest" in individual["name"] else 1

    @staticmethod
    def wrong_return_value(individual):
        return "wrong"

    @staticmethod
    def alter_individual(individual):
        individual["name"] += "-highest"
        return 0

    @staticmethod
    def i_think_none_of_it(individual):
        return None
