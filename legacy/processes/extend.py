from copy import deepcopy

from django.db import models

import jsonfield

from legacy.processes.register import RegisterContainer
from legacy.helpers.storage import get_hif_model
from legacy.exceptions import HIFImproperUsage
from legacy.helpers.data import reach, expand, interpolate
from legacy.helpers.enums import ProcessStatus as Status


class ExtensionContainer(RegisterContainer):  # TODO: tests!

    def extensions(self):
        """
        Should filter for all subs with an extends field set to this class
        """
        return self.attr("extension", cls=self._processes)


class Extend(models.Model):

    extensions = jsonfield.JSONField(null=True, blank=True, default=None)
    HIF_extension_statusses = [Status.DONE]

    def __init__(self, *args, **kwargs):
        super(Extend, self).__init__(*args, **kwargs)
        self.ext = None
        self.source = None

    class Meta:
        abstract = True

    def setup_fields(self, *args, **kwargs):
        super(Extend, self).setup_fields(*args, **kwargs)
        if self.extensions is None:
            self.ext = ExtensionContainer()
        else:
            self.ext = ExtensionContainer(self.register)

    def retain_fields(self):
        super(Extend, self).retain_fields()
        self.extensions = self.ext.dict() if self.ext.dict() else None

    def get_source(self, ser_extendee):

        if self.source is None:

            Extendee = get_hif_model(ser_extendee)
            extendee = Extendee().load(serialization=ser_extendee)

            # TODO: check existance _extend in config

            if 'source' not in self.config._extend:
                self.status = Status.ERROR
                raise HIFImproperUsage('Source path is not present in extend config during extending')

            self.source = reach(self.config._extend['source'], extendee.rsl)

        return self.source

    def extend(self, ser_extendee):
        """
        This method adds an entry called extending to the meta field
        That entry specifies how the results should be merged by extendee
        meta = {
            "extending": OriginalDict
        }
        """
        source = self.get_source(ser_extendee)

        # Setting the meta field with extending key will make extension property return other then None
        self.meta = {'extending': reach(self.config._extend['target'], source)}

    def extend_setups(self, ser_extendee):
        """

        """
        source = self.get_source(ser_extendee)

        # TODO: This should probably not be here. Write tests to confirm
        if not source:
            return []

        setups = []

        for args_path in expand(self.config._extend['args'], source):

            kwargs = deepcopy(self.config.dict(protected=True))
            args_data = reach(args_path, source)
            args = [args_data] if not isinstance(args_data, list) else args_data

            # Kwargs is config with extend kwargs
            if 'kwargs' in self.config._extend:
                for kw, kwpath in self.config._extend['kwargs'].iteritems():
                    interpolated_kwpath = interpolate(kwpath, args_path)
                    kwargs[kw] = reach(interpolated_kwpath, source)

            # Args from config might be a list of keypaths to use as args
            if 'target' in self.config._extend and self.config._extend['target'] is not None:
                kwargs['_extend']['target'] = interpolate(self.config._extend['target'], args_path)

            setups.append((args, kwargs,))

        return setups

    @property
    def extension(self):
        """
        Returns the target path that is supposed to be updated and the object to extend with.
        """
        extension = self.meta.get('extending') if self.meta is not None else None
        if extension is None:
            return None
        if self.config._extend["extension"] is not None:
            extension[self.config._extend["extension"]] = self.rsl
        else:
            extension = self.rsl
        return extension, self.config._extend["target"]

    def merge_extensions(self):
        """

        """
        for extension, path in self.ext.extensions():
            target = reach(path, self.rsl)
            target.update(extension)
        self.ext.empty()
