from django.db.models.loading import get_model

from HIF.exceptions import HIFImproperUsage


def get_hif_model(name):
    """
    Returns the class of a model with specified name.
    It fails if the model is not registered with HIF as app_label
    It also fails if the model is not imported in models folder/file
    """
    model = get_model(app_label="HIF", model_name=name)
    if model is None:
        raise HIFImproperUsage("The specified model does not exist, is not imported in models " +
                               "or is not registered as Django model with HIF label.")
    return model


def deserialize(serialization):
    """
    This function will check whether a serialization tuple has the correct format
    and returns the values in the tuple
    A valid tuple has the form ("ModelName", 0,) where 0 is the id of the object.
    """
    try:
        if not isinstance(serialization, tuple):
            raise HIFImproperUsage("Serialization is not a tuple.")
        if not isinstance(serialization[0], (unicode, str)):
            raise HIFImproperUsage("Model in serialization tuple is not stringish but {}.".format(
                type(serialization[0])))
        if not isinstance(serialization[1], (int, long, float, complex)):
            raise HIFImproperUsage("Object id in serialization is not an numberish, but {}.".format(
                type(serialization[1])))
    except IndexError:
        raise HIFImproperUsage("Serialization tuple is too short.")
    return serialization[0], serialization[1]


class Container(object):

    # Creation and typical Python functionality

    def __init__(self, init={}, *args, **kwargs):
        """
        Optionally takes a dict which will be used to set initial content of container.
        """
        super(Container, self).__init__(*args, **kwargs)
        self._container = {}
        self(init)
        #self._container = dict(init)  # TODO: naive to set like this, check existence of keys

    def __call__(self, dictionary):
        """
        Takes a dictionary
        Will check whether all keys are valid model names
        And whether all values are lists
        Then copies the item unto _container dict.
        """
        dictionary = dict(dictionary)
        for key, ids in dictionary.iteritems():
            try:
                get_hif_model(key)
            except HIFImproperUsage as exception:
                raise HIFImproperUsage(
                    "Dict given to Container contains a key {}, which raises an exception in get_hif_model".format(
                    key, str(exception)))
            if not isinstance(ids, list):
                raise HIFImproperUsage("Dict given to Container contains invalid value for key {}".format(key))
            # TODO: further check whether elements in list are ids?
            self._container[key] = ids

    def dict(self):
        """
        Simply returns inner representation of Container.
        """
        return self._container

    def __getitem__(self, cls):  # TODO: return Q instead?
        """
        Get item returns a QuerySet with all models who's ids are present in the list of ids.
        Raises exceptions when models don't exist or a non-existing key is given.
        """
        if not cls in self._container:
            raise KeyError("Container does not hold instances of {}".format(cls))
        model = get_hif_model(cls)
        return model.objects.filter(id__in=self._container[cls])

    # Extra functionality useful for models/classes who use Containers
    # Think about adding, removing, counting and executing functions.

    def add(self, ser):
        """
        Deserialize a serialization tuple
        Add class as a key if it doesn't exist or add id of object to list of ids
        """
        cls, obj_id = deserialize(ser)
        if cls not in self._container:
            get_hif_model(cls)  # checks existence of model or raises HIFImproperUsage
            self._container[cls] = [obj_id]
        elif obj_id not in self._container[cls]:
            self._container[cls].append(obj_id)

    def remove(self, ser):
        """
        Deserialize a serialization tuple
        Delete id from list and delete key if the list is empty.
        """
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
        model = get_hif_model(cls)
        return model.objects.filter(id__in=self._container[cls], **query_dict)

    def count(self, query_dict):
        count = 0
        for cls in self._container.iterkeys():
            count += self.query(cls, query_dict).count()
        return count

    # TODO: can you update query sets like this??
    def update(self, cls, update_dict):
        return self[cls].update(**update_dict)
