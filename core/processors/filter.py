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
        criteria = {  # TODO: use config.get instead
            key: getattr(self.config, key).split("|") for key in self.config.select_keys
            if getattr(self.config, key, None)
        }
        if not criteria:
            for individual in individuals:
                yield individual
        else:
            for individual in individuals:
                for key in criteria.keys():
                    if key in individual and individual[key] in criteria[key]:
                        break
                else:
                    continue
                yield individual
