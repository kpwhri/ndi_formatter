import collections
import itertools


def flatten_list(lst):
    for el in lst:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            for item in flatten_list(el):
                yield item
        else:
            yield el


def combinations(lst):
    for p in itertools.product(
            *[x if isinstance(x, collections.Iterable) and not isinstance(x, (str, bytes)) else [x] for x in lst]):
        yield p