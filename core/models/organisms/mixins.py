from core.processors.base import Processor


class ProcessorMixin(object):

    def prepare_process(self, process, async=False, extra_config=None):
        """
        Creates an instance of the processor based on requested process with a correct config set.
        Processors get loaded from core.processors
        It returns the processor and the method that should be invoked.

        :param process: A dotted string indicating the processor and method that represent the process.
        :return: processor, method
        """
        assert isinstance(extra_config, (dict, type(None))), \
            "Extra config given to prepare_process should be None or a dictionary"

        processor_name, method_name = process.split(".")
        processor_class = Processor.get_processor_class(processor_name)

        if processor_class is None:
            raise AssertionError(
                "Could not import a processor named {} "
                "from core.processors or sources.processors.".format(processor_name)
            )
        config = self.config.to_dict(protected=True)
        if extra_config is not None and isinstance(extra_config, dict):
            config.update(extra_config)
        processor = processor_class(config=config)
        method, args_type = processor.get_processor_method(method_name)
        if async:
            method = getattr(method, "delay")
        if not callable(method):
            raise AssertionError("{} is not a callable property on {}.".format(method_name, processor))
        return processor, method, args_type
