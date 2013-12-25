from django.db.models.loading import get_model

from HIF.exceptions import HIFImproperUsage


def get_hif_model(name):
    model = get_model(app_label="HIF", model_name=name)
    if model is None:
        raise HIFImproperUsage("The specified model does not exist or is not registered as Django model with HIF label.")
    return model

        ## Load fail wrong model
        #try:
        #    instance.load(("DoesNotExist", 1,))
        #    self.fail()
        #except HIFImproperUsage as exception:
        #    self.assertEqual(str(exception), "The specified model does not exist or is not registered as Django model with HIF label.")


def deserialize(serialization):
    try:
        assert isinstance(serialization, tuple), "HIFImproperUsage: serialization is not a tuple."
        assert isinstance(serialization[0], unicode) or isinstance(serialization[0], str), \
            "HIFImproperUsage: model name in serialization tuple is not a string but a {}.".format(type(serialization[0]))
        assert isinstance(serialization[1],int), \
            "HIFImproperUsage: object id in serialization is not an int, but a {}.".format(type(serialization[1]))
    except IndexError:
        raise HIFImproperUsage("Serialization tuple is too short.")
    return serialization[0], serialization[1]


class Container(object):

    def __init__(self, init={}, *args, **kwargs):
        super(Container, self).__init__(*args, **kwargs)
        self._container = dict(init)

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
