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
    if path and path.startswith("$"):  # TODO: fix now that legacy is gone
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
