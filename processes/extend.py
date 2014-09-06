from django.db import models

import jsonfield

from HIF.processes.register import RegisterContainer
from HIF.helpers.storage import get_hif_model
from HIF.exceptions import HIFImproperUsage
from HIF.helpers.data import reach
from HIF.helpers.enums import ProcessStatus as Status


class ExtensionContainer(RegisterContainer):  # TODO: tests!

    def extend(self):
        """
        Should filter for all subs with an extends field set to this class
        """
        pass


class Extend(models.Model):

    extensions = jsonfield.JSONField(null=True, blank=True, default=None)

    def __init__(self, *args, **kwargs):
        super(Extend, self).__init__(*args, **kwargs)
        self.ext = None

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

    def extend(self, ser_extendee):
        """
        This method looks at extend configuration and adjusts arguments and configuration of process based on that.


        This method adds an entry called extending to the meta field
        That entry specifies how the results should be merged by extendee
        meta = {
            "extending": OriginalDict
        }
        It also sets extends field for database filtering

        Should check statusses are in correct range

        This method returns raises exceptions if extendee can't be worked with
        """
        Extendee = get_hif_model(ser_extendee)
        extendee = Extendee().load(serialization=ser_extendee)  # TODO: write test that makes sure this function does not change extendee

        # TODO: make status checks possible by registering later
        #if extendee.status not in self.HIF_extension_statusses:
        #    self.status = Status.CANCELLED
        #    raise Exception('status is wrong!')

        if 'keypath' not in self.config._extend:
            self.status = Status.ERROR
            raise HIFImproperUsage('Keypath is not present in extend config during extending')

        source = reach(self.config._extend['keypath'], extendee.rsl)
        self.meta = {'extending': source}

        # Pad self.arguments with args from extend config
        if 'args' in self.config._extend:
            args = self.arguments or []
            for keypath in self.config._extend['args']:
                arg = reach(keypath, source)
                if arg not in args:
                    args.append(arg)
            self.arguments = args

        # Pad config with extend kwargs
        if 'kwargs' in self.config._extend:
            kwargs = {}
            for kw, keypath in self.config._extend['kwargs'].iteritems():
                kwargs[kw] = reach(keypath, source)
            self.config(kwargs)

    @property
    def extension(self):
        """
        Returns the keypath that is supposed to be replaced and the extended object
        """
        extension = self.meta['extending']
        extension[self.config._extend["extension"]] = self.rsl
        return self.config._extend["keypath"], extension
