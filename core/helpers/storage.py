from copy import deepcopy

from django.db.models.loading import get_model

from core.exceptions import HIFImproperUsage


def deserialize(serialization):
    """
    This function will check whether a serialization tuple has the correct format
    and returns the values in the tuple
    A valid serialization has the form ("ModelName", 0,) or ["ModelName", 0,] where 0 is the id of the object.
    """
    # TODO: remove tuple, since it is not Celery safe and unsupported.
    try:
        if not isinstance(serialization, (tuple, list)):
            raise HIFImproperUsage("Serialization is not a list or tuple.")
        if not isinstance(serialization[0], basestring):
            raise HIFImproperUsage("Model in serialization sequence is not stringish but {}.".format(
                type(serialization[0])))
        if not isinstance(serialization[1], (int, long, float, complex)):
            raise HIFImproperUsage("Object id in serialization is not an numberish, but {}.".format(
                type(serialization[1])))
    except IndexError:
        raise HIFImproperUsage("Serialization tuple is too short.")
    return serialization[0], serialization[1]


def get_hif_model(inp):  # TODO: tests!
    """
    Returns the class of a model with specified name.
    Takes a serialized process or a model name as input

    It fails if the model is not registered with HIF as app_label
    It also fails if the model is not imported in models folder/file
    """
    if not isinstance(inp, basestring):
        name, prc_id = deserialize(inp)
    else:
        name = inp

    model = get_model(app_label="HIF", model_name=name)
    if model is None:
        raise HIFImproperUsage("The specified model does not exist, is not imported in models " +
                               "or is not registered as Django model with HIF label.")
    return model


def copy_hif_model(model):  # TODO: tests!
    """

    """
    cpy = deepcopy(model)  # TODO: necessary?
    cpy.pk = None
    cpy.id = None
    cpy.save()
    return cpy


class Container(object):

    # Creation and typical Python functionality

    def __init__(self, init={}, *args, **kwargs):
        """
        Optionally takes a dict which will be used to set initial content of container.
        """
        super(Container, self).__init__(*args, **kwargs)
        self._container = {}
        self(init)

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
        return cls  # TODO: keep? add to tests!

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
        return cls  # TODO: keep? add to tests!

    def run(self, method, cls=None, *args, **kwargs):  # TODO: test new flexible cls argument
        """
        Calls specified method on all instances of cls saved in Container.
        It doesn't do a valid arguments check, not even an attribute check.
        """
        methods = self.attr(method, cls=cls)
        for method in methods:
            method(*args, **kwargs)

    def attr(self, attr, cls=None):  # TODO: tests!
        """

        """
        if cls is not None:
            classes = [cls] if not isinstance(cls, (tuple, list)) else cls
        else:
            classes = list(self.dict())

        attrs = []
        for cls in classes:
            for obj in self[cls]:
                obj.setup()
                obj_attr = getattr(obj, attr)
                if obj_attr is not None:
                    attrs.append(obj_attr)

        return attrs

    def query(self, cls, query_dict):
        """
        Gets a query set with all models who's ids are in ids list.
        And applies the additional query_dict filters on that query set in an AND fashion.
        """
        model = get_hif_model(cls)
        return model.objects.filter(id__in=self._container[cls], **query_dict)

    def count(self, query_dict):
        """
        Counts all objects of all models that are somehow stored in this Container
        and who also match the query_dict parameters
        """
        count = 0
        for cls in self._container.iterkeys():
            count += self.query(cls, query_dict).count()
        return count

    def empty(self):
        self._container = {}