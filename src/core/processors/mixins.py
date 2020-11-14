import warnings

from core.processors.base import Processor


class ProcessorMixin(object):

    def prepare_process(self, process, asynchronous=False, class_config=None):
        """
        Creates an instance of the processor based on requested process with a correct config set.
        Processors get loaded from core.processors
        It returns the processor and the method that should be invoked.

        :param process: A dotted string indicating the processor and method that represent the process.
        :param asynchronous: Whether to process asynchronously or not
        :param class_config: The configuration that should be used to supplement the processor configuration
        :return: processor, method
        """
        assert isinstance(class_config, (dict, type(None))), \
            "Class config given to prepare_process should be None or a dictionary"
        if class_config is not None:
            self.config.supplement(class_config)

        processor_name, method_name = Processor.get_processor_components(process)
        processor = Processor.create_processor(processor_name, self.config.to_dict(protected=True))
        method, args_type = processor.get_processor_method(method_name)
        if asynchronous:
            method = getattr(method, "delay")
        if not callable(method):
            raise AssertionError("{} is not a callable property on {}.".format(method_name, processor))
        return processor, method, args_type
