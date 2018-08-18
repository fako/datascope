from datagrowth.docs.pipelines.base import DataProcess
from datagrowth.docs.pipelines.inputs import Input
from datagrowth.docs.pipelines.outputs import Output


class Payload(DataProcess, Input, Output):
    pass
