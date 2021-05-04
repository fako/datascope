from datagrowth.configuration import ConfigurationProperty
from datagrowth.resources.shell.tasks import run, run_serie
from core.processors.resources.base import ResourceProcessor


class ShellResourceProcessor(ResourceProcessor):

    ARGS_BATCH_METHODS = ['run_mass']

    config = ConfigurationProperty(
        namespace="shell_resource",
        private=["_resource"]
    )

    #######################################################
    # TASKS
    #######################################################
    # Wrappers that act as an interface
    # to background retrieval of resources

    @property
    def run(self):
        return run.s(
            config=self.config.to_dict(private=True, protected=True)
        )

    @property
    def run_mass(self):
        return run_serie.s(
            config=self.config.to_dict(private=True, protected=True)
        )
