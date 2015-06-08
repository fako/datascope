from __future__ import unicode_literals, absolute_import, print_function, division

import json
import copy
from collections import Counter


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
    if path and path.startswith("$"):  # backward compatibility for "legacy" algorithms
        if len(path) > 1:
            path = path[2:]
        else:
            path = None

    # First we check whether we really get a structure we can use
    if path is None:
        return data
    if not isinstance(data, (dict, list, tuple)):
        raise TypeError("Reach needs dict, list or tuple as input, got {} instead".format(type(data)))

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


def interpolate(interpolate_path, source_path):
    """

    :param path1:
    :param path2:
    :return:
    """
    interpolate_parts = interpolate_path.split('.')
    source_parts = source_path.split('.')
    parts = []

    for interpolate_part, source_part in zip(interpolate_parts, source_parts):
        if interpolate_part == '*':
            if not source_part.isdigit():
                raise ValueError("Can't interpolate * with non-digit value '{}'.".format(source_part))
            parts.append(source_part)
        elif interpolate_part == source_part:
            parts.append(interpolate_part)
        else:
            raise ValueError("Can't interpolate {} with {}, because paths differ at {}/{}.".format(
                interpolate_path,
                source_path,
                interpolate_part,
                source_part
            ))

    if len(parts) < len(interpolate_parts):
        parts += interpolate_parts[len(parts):]

    return '.'.join(parts)


def expand(keypath, data):  # TODO: handle exceptions better like dotted.key etc.
    """

    :param path:
    :param data:
    :return:
    """
    paths = [keypath] if not isinstance(keypath, list) else keypath
    new = []

    for path in paths:
        pth = None

        for part in path.split('.'):

            if part == '*':  # TODO: prevent dict access here
                for ind, value in enumerate(reach(pth, data)):
                    new_path = path.replace('*', str(ind), 1)
                    new.append(new_path)
                break
            else:
                pth = part if pth is None else pth + '.' + part

    if new:
        return expand(new, data)
    else:
        return paths


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


def count_2d_list(data, d1_id=None, d2_list=None, d2_id=None, weight=None):  # TODO: test!
    """

    """

    if not isinstance(data, (list, tuple)):
        raise TypeError('count_2d_list expects to get a list as input.')

    results = Counter()

    for d1_row in data:

        d2_data = reach(d2_list, d1_row)

        if d2_data is not None and not isinstance(d2_data, (list, tuple)):
            raise TypeError(
                'count_2d_list expects the d2_list keypath to yield a list or tuple got {} instead.'.format(
                    type(d2_data)
                )
            )
        if d2_id is not None:
            results += Counter([data[d2_id] for data in d2_data])
        else:
            results += Counter(d2_data)  # TODO: add weight of lists with something like: weight[d1_id] * d2_data

    return results
