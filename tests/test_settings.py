# -*- coding: utf-8 -*-
"""
tests.test_settings
~~~~~~~~~~~~~~~~~~~

Tests how settings are constructed and overriden.

"""
from jobber.conf import _Settings


def test_settings():
    one = {'FOO': 'bar'}
    two = {'FOOZ': 'barz'}
    settings = _Settings(one, two)
    assert settings.FOO == 'bar'
    assert settings.FOOZ == 'barz'


def test_settings_override():
    one = {'FOO': 'bar'}
    settings = _Settings(one)
    assert settings.FOO == 'bar'

    override = {'FOO': 'wat'}
    settings.apply(override)
    assert settings.FOO == 'wat'