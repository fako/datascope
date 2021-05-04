from datagrowth.configuration import DEFAULT_CONFIGURATION, ConfigurationProperty
from datagrowth.resources.shell.tasks import run, run_serie
from core.processors.resources.base import ResourceProcessor


class ShellResourceProcessor(ResourceProcessor):

    ARGS_BATCH_METHODS = ['run_mass']

    config = ConfigurationProperty(
        storage_attribute="_config",
        defaults=DEFAULT_CONFIGURATION,
        private=["_resource"],
        namespace="shell_resource"
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
