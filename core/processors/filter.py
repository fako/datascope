from core.processors.base import Processor


class FilterProcessor(Processor):

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
