from core.processors.base import Processor


class FilterProcessor(Processor):

    def distinct(self, individuals):
        # TODO: do not do this in memory?
        yields = set()
        for individual in individuals:
            if not self.config.distinct_key in individual:
                yield individual
            elif individual[self.config.distinct_key] not in yields:
                yields.add(individual[self.config.distinct_key])
                yield individual
