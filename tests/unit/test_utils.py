# -*- coding: utf-8 -*-
"""
tests.unit.test_utils
~~~~~~~~~~~~~~~~~~~~~

Tests for utility functions.

"""
import pytest
from jobber.core import utils
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


def test_mapping():
    mapping = utils.Mapping({
        1: 'foo',
        2: 'bar'
    })
    assert 1 in mapping
    assert 2 in mapping
    assert mapping[1] == 'foo'
    assert mapping[2] == 'bar'
    assert mapping.map(1) == 'foo'
    assert mapping.map(2) == 'bar'
    assert mapping.inverse('foo') == 1
    assert mapping.inverse('bar') == 2
    assert mapping.items() == [(1, 'foo'), (2, 'bar')]


def test_tag_parser():
    assert utils.parse_tags('') == []
    assert utils.parse_tags(None) == []
    assert utils.parse_tags('one') == ['one']
    assert utils.parse_tags('one, two') == ['one', 'two']
    assert utils.parse_tags('one,two') == ['one', 'two']
    assert utils.parse_tags('one,two,two') == ['one', 'two']
    assert utils.parse_tags('one two', delim=' ') == ['one', 'two']


@pytest.mark.parametrize('input,expected', [
    ('<div>a</div>', '<div>a</div>'),
    ('<div class="b">a</div>', '<div>a</div>'),
    ('<a href="b">a</a>', '<a href="b">a</a>'),
    ('<script>a</script>', 'a'),
    ('<script src="b">a</script>', 'a'),
])
def test_clean_html(input, expected):
    assert utils.clean_html(input) == expected


@pytest.mark.parametrize('input,expected', [
    ('<div>a</div>', 'a'),
    ('<div class="b">a</div>', 'a'),
    ('<a href="b">a</a>', 'a'),
    ('<script>a</script>', 'a'),
    ('<script src="b">a</script>', 'a'),
])
def test_strip_html(input, expected):
    assert utils.strip_html(input) == expected


@pytest.mark.parametrize('input,expected', [
    ('http://example.com', 'http://example.com'),
    ('https://example.com', 'https://example.com'),
    ('ftp://example.com', 'ftp://example.com'),
    ('example.com', 'http://example.com'),
    ('', ''),
    (None, None),
])
def test_ensure_protocol(input, expected):
    assert utils.ensure_protocol(input) == expected
