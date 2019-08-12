from __future__ import unicode_literals, absolute_import, print_function, division

import operator
import math
from itertools import islice, cycle
from functools import reduce

from django.apps import apps as django_apps

from datagrowth.utils import parse_datetime_string, format_datetime, override_dict



def get_any_model(name):  # TODO: test to unlock
    try:
        app_label, model = next(
            (model._meta.app_label, model.__name__)
            for model in django_apps.get_models() if model.__name__ == name
        )
    except StopIteration:
        raise LookupError("Could not find {} in any app_labels".format(name))
    return django_apps.get_model(app_label, name)


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
                raise


def ibatch(iterable, batch_size):  # TODO: test to unlock, should be deprecated in favour of datagrowth.utils.ibatch
    it = iter(iterable)
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            return
        yield batch


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


def batchize(elements, batch_size):  # TODO: test to unlock, should be deprecated in favour of datagrowth.utils.ibatch
    batches = int(math.floor(elements / batch_size))
    rest = elements % batch_size
    if rest:
        batches += 1
    return batches, rest
