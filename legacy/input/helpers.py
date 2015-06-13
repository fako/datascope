# TODO: test this!
def sanitize_single_trueish_input(to_check, class_name='Class'):

    if isinstance(to_check, (list, tuple,)):

        if not len(to_check) == 1:
            return False, "{} should receive one input through args parameter it received {}.".format(class_name, len(to_check))
        if not to_check[0]:
            return False, "{} was given a falsy value".format(class_name)

        return True, to_check[0]

    else:

        if to_check:
            return True, to_check
        else:
            return False, "{} was given a falsy value".format(class_name)