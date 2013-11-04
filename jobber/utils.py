"""
jobber.utils
~~~~~~~~~~~~

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
