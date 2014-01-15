# -*- coding: utf-8 -*-
"""
tests.unit.test_signals
~~~~~~~~~~~~~~~~~~~~~~~

Tests signal functions.

"""
import pytest
from mock import MagicMock

from jobber.core.models import Job, Company, Location


class TestObject(object):
    pass


class AnotherTestObject(object):
    pass


@pytest.fixture(scope='function')
def location():
    return Location(city=u'Lïｍáｓѕ߀ɭ', country_code='CYP')


@pytest.fixture(scope='function')
def company():
    return Company(name=u'remedica')


@pytest.fixture(scope='function')
def job(company, location):
    return Job(id=1,
               title='testfoo',
               description='testfoo',
               contact_method=1,
               remote_work=False,
               company=company,
               location=location,
               job_type=1,
               recruiter_name=u'jon',
               recruiter_email=u'doe')


@pytest.fixture(scope='function')
def actionmap(monkeypatch):
    """Creates a test model action map and patches the existing one."""
    from jobber import signals

    test_actionmap = {
        TestObject: {
            'insert': ['on_insert_foo', 'on_insert_bar'],
            'update': ['on_update_baz']
        }
    }

    monkeypatch.setattr(signals, 'DEFAULT_MODEL_ACTIONMAP', test_actionmap)
    monkeypatch.setattr(signals, 'on_insert_foo', MagicMock(), raising=False)
    monkeypatch.setattr(signals, 'on_insert_bar', MagicMock(), raising=False)
    monkeypatch.setattr(signals, 'on_update_baz', MagicMock(), raising=False)

    return test_actionmap


def test_find_model_actions(app, actionmap):
    from jobber import signals

    actions = signals.find_model_actions(TestObject, 'insert')
    assert actions == [signals.on_insert_foo, signals.on_insert_bar]

    actions = signals.find_model_actions(TestObject, 'update')
    assert actions == [signals.on_update_baz]

    actions = signals.find_model_actions(TestObject, 'delete')
    assert actions == []

    actions = signals.find_model_actions(AnotherTestObject, 'insert')
    assert actions == []


def test_on_models_committed(app, actionmap):
    from jobber import signals

    changes = [(TestObject(), 'insert')]
    signals.on_models_committed(app, changes)

    assert signals.on_insert_foo.called
    assert signals.on_insert_bar.called
    assert not signals.on_update_baz.called
