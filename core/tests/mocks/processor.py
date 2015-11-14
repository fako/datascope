from core.utils.configuration import ConfigurationProperty
from datascope.configuration import MOCK_CONFIGURATION


class MockProcessor(object):

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=MOCK_CONFIGURATION,
        namespace="mock_processor",
        private=[]
    )

    def __init__(self, config):
        super(MockProcessor, self).__init__()
        self.config = config


class MockNumberProcessor(MockProcessor):

    def number_individuals(self, individuals):
        for index, individual in enumerate(individuals):
            individual["number"] = index + 1
        return individuals


class MockFilterProcessor(MockProcessor):

    def filter_individuals(self, individuals):
        results = []
        for individual in individuals:
            if self.config.include_odd and individual.get("number") % 2:
                results.append(individual)
            elif self.config.include_even and not individual.get("number") % 2:
                results.append(individual)
            elif self.config.include_odd and self.config.include_even:
                results.append(individual)
        return results