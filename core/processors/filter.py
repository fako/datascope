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

    def select(self, individuals):
        keys = self.config.select_keys
        for individual in individuals:
            for key in keys:
                value = getattr(self.config, key, None)  # TODO: use config.get instead
                if value is not None and key in individual and individual[key] == value:
                    break
            else:
                continue
            yield individual
