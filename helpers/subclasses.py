from django.db.models.loading import get_model

from HIF.helpers.enums import ProcessStatus
from HIF.exceptions import HIFContainerError, HIFImproperUsage
from HIF.models.settings import Domain


def deserialize(serialization):
    try:
        assert isinstance(serialization, tuple), "HIFImproperUsage: serialization is not a tuple."
        assert isinstance(serialization[0], unicode) or isinstance(serialization[0], str), "HIFImproperUsage: model name in serialization tuple is not an unicode."
        assert isinstance(serialization[1],int), "HIFImproperUsage: object id in serialization is not an int."
    except IndexError:
        raise HIFImproperUsage("Serialization tuple is too short.")
    return serialization[0], serialization[1]


class Config(object):  # TODO: tests

    _private = ["_private", "_domain", "_namespace"]

    def __init__(self, namespace, private):
        super(Config, self).__init__()
        self._domain = Domain()
        self._namespace = namespace
        self._private += [prv for prv in private if prv not in self._private]

    def __getattr__(self, item):
        if hasattr(self._domain, self._namespace + '_' + item):
            return getattr(self._domain, self._namespace + '_' + item)
        else:
            raise AttributeError("Tried to retrieve '{}' in config and namespace '{}', without results.".format(item, self._namespace))

    def __call__(self, new):
        for key, value in new.iteritems():
            setattr(self, key, value)

    def __str__(self):
        return str(self.dict())

    def dict(self, protected=False, private=False):
        dictionary = dict()
        for key, value in self.__dict__.iteritems():
            if key == '_domain':
                continue
            if key.startswith('_'):
                if (private and key in self._private) or (protected and key not in self._private):
                    dictionary[key] = value
            else:
                dictionary[key] = value
        return dictionary




class Container(object):

    def __init__(self, init={}, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self._container = dict(init)
        self._updated = False

    def __getitem__(self, cls):  # TODO: return Q instead?
        if not cls in self._container:
            raise KeyError("Container does not hold instances of {}".format(cls))
        model = get_model(app_label="HIF", model_name=cls)
        if model is None:
            raise HIFImproperUsage("The specified model does not exist or is not registered as Django model with HIF label.")
        return model.objects.filter(id__in=self._container[cls])

    def dict(self):
        return self._container

    def __call__(self, dictionary):
        self._container = dict(dictionary)


    def add(self, ser):
        cls, obj_id = deserialize(ser)
        if cls not in self._container:
            self._container[cls] = [obj_id]
        elif obj_id not in self._container[cls]:
            self._container[cls].append(obj_id)
        self._updated = True

    def remove(self, ser):
        cls, obj_id = deserialize(ser)
        if cls in self._container and obj_id in self._container[cls]:
            self._container[cls].remove(obj_id)
            if not self._container[cls]:
                del self._container[cls]


    def run(self, cls, method, *args, **kwargs):
        for obj in self[cls]:
            obj.setup()
            getattr(obj, method)(*args, **kwargs)

    def query(self, cls, query_dict):
        model = get_model(app_label="HIF", model_name=cls)
        if model is None:
            raise HIFImproperUsage("The specified model does not exist or is not registered as Django model with HIF label.")
        return model.objects.filter(id__in=self._container[cls], **query_dict)

    def count(self, query_dict):
        count = 0
        for cls in self._container.iterkeys():
            count += self.query(cls, query_dict).count()
        return count

    def update(self, cls, update_dict):
        return self[cls].update(**update_dict)




#class ProcessContent(Content):
#
#    def execute(self, process):
#        for prc in self[process]:
#            prc.execute()
#
#    def subscribe(self, process, to):
#        for prc in self[process]:
#            prc.subscribe(to)
#
#    def errors(self):
#        count = 0
#        for key, prc_ids in self._virtual.iteritems():
#            typ, con_id = key
#            con = ContentType.objects.get_for_id(con_id).model_class()
#            count += con.objects.filter(id__in=prc_ids,status__in=[ProcessStatus.ERROR, ProcessStatus.WARNING]).count()
#        return count
#
#    def waiting(self):
#        count = 0
#        for key, prc_ids in self._virtual.iteritems():
#            typ, con_id = key
#            con = ContentType.objects.get_for_id(con_id).model_class()
#            count += con.objects.filter(id__in=prc_ids,
#                status__in=[ProcessStatus.WAITING, ProcessStatus.SUBSCRIBED, ProcessStatus.READY]).count()
#        return count



