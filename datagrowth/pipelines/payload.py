from datagrowth.pipelines.base import DataProcess
from datagrowth.pipelines.inputs import Input
from datagrowth.pipelines.outputs import Output


class Payload(DataProcess, Input, Output):
    pass
