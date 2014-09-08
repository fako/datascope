import json
import copy


def reach(path, data):
    """
    Reach takes a data structure and a path. It will return the value belonging to the path,
    the value under a key containing dots mistaken for a path or None if nothing can be found.

    Paths are essentially multiple keys or indexes separated by '.'
    Each part of a path is another level in the structure given.
    For instance with a structure like
    {
        "test": {"test": "second level test"},
        "list of tests": ["test0","test1","test2"]
    }
    "test.test" as path would return "second level test"
    while "test.1" as path would return "test1"
    """

    # First we check whether we really get a structure we can use
    if path is None:  # TODO: write a test for this behavior
        return data
    if not isinstance(data, (dict, list, tuple)):
       raise TypeError("Reach needs dict as input, got {} instead".format(type(data)))

    # We make a copy of the input for later reference
    root = copy.deepcopy(data)

    # We split the path and see how far we get with using it as key/index
    try:
        for part in path.split('.'):
            if part.isdigit():
                data = data[int(part)]
            else:
                data = data[part]
        else:
            return data

    except (IndexError, KeyError, TypeError):
        pass

    # We try the path as key/index or return None.
    path = int(path) if path.isdigit() else path
    return root[path] if path in root else None


def extractor(target, objective):
    """
    This function takes a data construct and a dictionary (objective)
    From the data it tries to create instances like the objective
    Whenever it encounters a key from the dict in the data it will initiate a new copy of the dict
    And fill the rest of the keys with values coming from the same keys present in data construct.

    The function will create a set of triggers from the keys of objective. When one of the triggers is found
    in the keys of the structure it is a signal to make a copy of the default dictionary given.
    Next it will look for keys on objective to override the default values.
    Any keys starting with _ will be excluded from the trigger list, but still used to extract data once extraction is
    triggered by another key that is in triggers.

    It is possible to pass a path as a key, in fact all keys on objective are considered paths and are given to reach().
    That function is responsible for finding all necessary data.
    """

    # General preparation
    results = []
    defaults = dict(objective)
    paths = [path if not path.startswith('_') else path[1:] for path in objective.iterkeys()]
    triggers = set([path.split('.')[0] for path in objective.iterkeys() if not path.startswith('_')])

    # Function which calls itself when necessary
    def extract(target):

        # Recursively use this function when confronted with list
        if isinstance(target, list):
            for index in target:
                extract(index)

        # Extract data when confronted with dict
        elif isinstance(target, dict):
            for key in target.iterkeys():
                # When a key in target is a trigger , create default result from objective
                # and reach for all paths in paths to fill result.
                if key in triggers:
                    result = dict(defaults)
                    updated = False
                    for path in paths:
                        reached = reach(path, target)
                        if reached is not None:
                            result[path] = reached
                            updated = True
                    if updated:
                        results.append(result)
                    break
                # Recursively use self when confronted with something else than a trigger
                else:
                    extract(target[key])

        # Only return the value when not dealing with lists or dicts.
        else:
            return target

    extract(target)
    return results


def json_extractor(json_string, objective):
    """
    This function turns a JSON string into python data and passes it to extractor()
    """
    try:
        target_dict = json.loads(json_string)
    except ValueError:
        # TODO: emit warning
        # No JSON could be decoded
        # We're unable to extract from that, so returning empty list
        return []
    return extractor(target_dict, objective)
