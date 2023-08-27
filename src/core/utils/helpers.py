import operator
from itertools import islice, cycle
from functools import reduce

from django.apps import apps as django_apps

from datagrowth.utils import parse_datetime_string, format_datetime, override_dict


def merge_iter(*iterables, **kwargs):  # TODO: test to unlock, works bad with empty iterables (don't flush RankProcessor.score at end for instance)
    """
    Given a set of reversed sorted iterables, yield the next value in merged order
    Takes an optional `key` callable to compare values by.

    Based on: http://stackoverflow.com/questions/14465154/sorting-text-file-by-using-python/14465236#14465236
    """
    key_func = operator.itemgetter(0) if 'key' not in kwargs else lambda item, key=kwargs['key']: key(item[0])
    order_func = min if 'reversed' not in kwargs or not kwargs['reversed'] else max

    iterables = [iter(it) for it in iterables]
    iterables = {i: [next(it), i, it] for i, it in enumerate(iterables)}
    while True:
        value, i, it = order_func(iterables.values(), key=key_func)
        yield value
        try:
            iterables[i][0] = next(it)
        except StopIteration:
            del iterables[i]
            if not iterables:
                return


def iroundrobin(*iterables):  # TODO: test to unlock
    "iroundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))


def cross_combine(first, second):  # TODO: test to unlock
    for primary in first:
        for secondary in second:
            yield (primary, secondary)


def cross_combine_2(*args):  # NB: beta

    if len(args) == 1:
        return ((primary,) for primary in args[0])

    def dual_combine(first, second):
        for primary in first:
            for secondary in second:
                yield (primary, secondary)

    return reduce(dual_combine, args)
