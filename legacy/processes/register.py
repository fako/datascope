import json

from django.db import models

import jsonfield

from legacy.helpers.storage import Container, get_hif_model
from legacy.helpers.enums import ProcessStatus as Status


class RegisterContainer(Container):  # TODO: tests!

    def __init__(self, *args, **kwargs):
        super(RegisterContainer, self).__init__(*args, **kwargs)
        self._processes = []
        self._texts = []
        for cls in list(self._container):
            self.register_type(cls)

    def __call__(self, *args, **kwargs):
        super(RegisterContainer, self).__call__(*args, **kwargs)
        self._processes = []
        self._texts = []
        for cls in list(self._container):
            self.register_type(cls)

    def register_type(self, cls):
        if cls in self._processes or cls in self._texts:
            return
        model = get_hif_model(cls)
        class_names = [mro.__name__ for mro in model.__mro__]
        if "ProcessStorage" in class_names:
            self._processes.append(cls)
        elif "TextStorage" in class_names:
            self._texts.append(cls)

    def add(self, ser):
        cls = super(RegisterContainer, self).add(ser)
        self.register_type(cls)

    def remove(self, ser):
        cls = super(RegisterContainer, self).remove(ser)
        self._processes.remove(cls)
        self._texts.remove(cls)

    def empty(self):
        super(RegisterContainer, self).empty()
        self._processes = []
        self._texts = []

    def errors(self):
        return self.count({"status__in": [Status.ERROR, Status.WARNING]})

    def waiting(self):
        return self.count({"status__in": [Status.PROCESSING, Status.WAITING, Status.READY]})

    def cancelled(self):
        return self.count({"status": Status.CANCELLED})

    def reports(self):
        reports = []
        for cls in self._processes:
            rprts = self.query(cls, {"status": Status.ERROR}).values_list('meta', flat=True)
            reports += [json.loads(rprt) for rprt in rprts if rprt]
        return reports

    def execute(self):
        if self._processes:
            self.run('execute', cls=self._processes)


class Register(models.Model):

    register = jsonfield.JSONField(null=True, blank=True, default=None)

    def __init__(self, *args, **kwargs):
        super(Register, self).__init__(*args, **kwargs)
        self.rgs = None

    class Meta:
        abstract = True

    def setup_fields(self, *args, **kwargs):
        super(Register, self).setup_fields(*args, **kwargs)
        if self.register is None:
            self.rgs = RegisterContainer()
        else:
            self.rgs = RegisterContainer(self.register)

    def retain_fields(self):
        super(Register, self).retain_fields()
        self.register = self.rgs.dict() if self.rgs.dict() else None

    def update_status(self):

        if self.status == Status.WAITING:
            self.rgs.execute()

        if self.rgs.waiting() != 0:
            self.status = Status.WAITING
        elif self.rgs.waiting() == 0:
            self.status = Status.READY

        if self.rgs.errors() != 0:
            self.status = Status.WARNING
