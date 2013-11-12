"""
jobber.core.utils
~~~~~~~~~~~~~~~~~

Utility methods.

"""
import re
from functools import reduce
from datetime import datetime
from unicodedata import normalize

import pytz


PUNCTUATION_REGEX = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def compose(*funcs):
    """Returns a function composition comprising of `funcs`. For example,
    compose(f, g)(x) = f(g(x)).

    :param funcs: Function splats.

    """
    def compose2(f, g):
        return lambda x: f(g(x))
    return reduce(compose2, funcs)


def slugify(text, delim='-', limit=75):
    """Slugifies `text` by applying the following transformations:

    * all lowercase letters
    * replace spaces with `delim`
    * remove puncuation marks
    * limit the length of `text` to <= `limit`

    :param text: A unicode string to slugify.

    """
    if isinstance(text, str):
        text = unicode(text, 'utf-8')
    words = []
    for word in PUNCTUATION_REGEX.split(text.lower()):
        clean = normalize('NFKD', word)
        if clean:
            words.append(clean)
    truncated = delim.join(words)[:limit]
    if truncated.endswith('-'):
        truncated = truncated[:-1]
    return truncated


def now():
    """Returns `utcnow()` as timezone-aware."""
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def transpose_dict(d):
    """Returns a dict where values become keys and keys values."""
    return {v: k for k, v in d.iteritems()}


class Mapping(object):
    """A convenient wrapper dict-like object which provides a two-way mapping
    from a `dict`.

    At this point, the `Mapping` class supports only one-to-one mappings.

    >>> mapping = Mapping({1: 'Link'})
    >>> mapping.map(1)
    ... 'Link'
    >>> mapping.inverse('Link')
    ... 1

    """
    def __init__(self, mapping):
        self.mapping = mapping
        self.mapping_transposed = transpose_dict(mapping)

    def __getitem__(self, key):
        return self.mapping[key]

    def __contains__(self, key):
        return key in self.mapping

    def __len__(self):
        return len(self.mapping)

    def map(self, key):
        return self.mapping[key]

    def inverse(self, key):
        return self.mapping_transposed[key]

    def items(self):
        return self.mapping.items()

