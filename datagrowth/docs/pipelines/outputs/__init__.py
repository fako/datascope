from datagrowth.pipelines.base import DataProcess


class Output(object):
    destination = None


class Append(DataProcess, Output):
    pass


class Update(DataProcess, Output):
    pass


class Inline(DataProcess, Output):
    pass
