# -*- coding: utf-8 -*-
"""
tests.unit.test_signals
~~~~~~~~~~~~~~~~~~~~~~~

Tests signal functions.

"""
import pytest
from mock import MagicMock

from jobber.models import Job, Company, Location


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


def test_find_model_actions():
    from jobber.core import signals

    actions = signals.find_model_actions(Job, 'insert')
    assert actions == [signals.update_jobs_index, signals.send_instructory_email]

    actions = signals.find_model_actions(Job, 'delete')
    assert actions == []


def test_on_models_committed_no_actions(monkeypatch, app):
    from jobber.core import signals

    mock = MagicMock()
    monkeypatch.setattr(signals, 'update_jobs_index', mock)

    company = Company(name='foocorp')
    changes = [(company, 'insert')]

    signals.on_models_committed(app, changes)

    assert not mock.called


def test_on_models_committed_job_model_not_published(monkeypatch, job, app):
    from jobber.core import signals

    mock_index = MagicMock(signals.Index)
    monkeypatch.setattr('jobber.core.signals.Index', mock_index)

    changes = [(job, 'insert')]
    signals.on_models_committed(app, changes)

    instance = mock_index.return_value
    assert not instance.add_document.called


def test_on_models_committed_job_model_published(monkeypatch, job, app):
    from jobber.core import signals

    mock_index = MagicMock(signals.Index)
    monkeypatch.setattr('jobber.core.signals.Index', mock_index)

    job.published = True
    changes = [(job, 'insert')]
    signals.on_models_committed(app, changes)

    instance = mock_index.return_value
    assert instance.add_document.called
