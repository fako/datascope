def override_dict(parent, child):
    # TODO: type checking?
    # TODO: test
    return dict(parent.copy(), **child)