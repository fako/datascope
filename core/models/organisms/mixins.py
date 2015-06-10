class ProcessorMixin(object):

    def prepare_process(self, process):
        """
        Creates an instance of the processor based on requested process with a correct config set.
        Processors get loaded from core.processors
        It returns the processor and the method that should be invoked.

        :param process: A dotted string indicating the processor and method that represent the process.
        :return: processor, method
        """
        import core.processors
        import sources.processors

        processor_name, method_name = process.split(".")
        try:
            core_class = getattr(core.processors, processor_name)
            sources_class = getattr(sources.processors, processor_name, None)
            processor_class = sources_class if sources_class else core_class
        except AttributeError:
            raise AssertionError(
                "Could not import a processor named {} "
                "from core.processors or sources.processors.".format(processor_name)
            )
        processor = processor_class(config=self.config.to_dict(protected=True))
        method = getattr(processor, method_name)
        if not callable(method):
            raise AssertionError("{} is not a callable property on {}.".format(method_name, processor))
        return processor, method