# -*- coding: utf-8 -*-
"""
tests.test_utils
~~~~~~~~~~~~~~~~

Tests for utility functions

"""
from jobber import utils
from unicodedata import normalize


def test_compose():
    f = lambda x: x ** 2
    g = lambda x: x * 4
    h = lambda x: x + 3

    c = utils.compose(g, f)
    assert c(2) == 16

    c = utils.compose(g, f, h)
    assert c(2) == 100


def test_slugify_non_unicode():
    slug = utils.slugify('test')
    assert isinstance(slug, unicode)
    assert slug == u'test'


def test_slugify_defaults():
    slug = utils.slugify(u'a b c')
    assert slug == u'a-b-c'

    slug = utils.slugify(u'Vìèt Nâm')
    assert slug == normalize('NFKD', u'vìèt-nâm')

    word = ' '.join(['a'] * 80)
    slug = utils.slugify(word)
    assert len(slug) <= 75
    assert slug[:-1] != '-'

    slug = utils.slugify(u'')
    assert slug == u''


def test_slugify_custom_delim():
    slug = utils.slugify(u'Vìèｔ Nâｍ', delim='+')
    assert slug == normalize('NFKD', u'vìèt+nâm')


def test_slugify_custom_limit():
    slug = utils.slugify(u'a b c d e f g', limit=4)
    assert slug == u'a-b'


def test_transpose_dict():
    d = {'1': 'a', '2': 'b'}
    t = utils.transpose_dict(d)
    assert 'a' in t
    assert 'b' in t
    assert '1' not in t
    assert '2' not in t
