from datagrowth.docs.pipelines.base import DataProcess


class Input(object):

    def __call__(self, *args, **kwargs):
        pass


class Generate(DataProcess, Input):
    pass


class Filesystem(Generate):
    pass


class Reference(DataProcess, Input):
    at = None
