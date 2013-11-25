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
def location(session):
    location = Location(city=u'Lïｍáｓѕ߀ɭ', country_code='CYP')
    session.add(location)
    session.flush()
    return location


@pytest.fixture(scope='function')
def company(session):
    company = Company(name=u'remedica')
    session.add(company)
    session.flush()
    return company


@pytest.fixture(scope='function')
def job(session, company, location):
    job = Job(title='testfoo',
              description='testfoo',
              contact_method=1,
              remote_work=False,
              company_id=company.id,
              location_id=location.id,
              job_type=1)
    session.add(job)
    session.flush()
    return job


def test_find_actions():
    from jobber.core import signals

    actions = signals.find_actions(Job, 'insert')
    assert actions == [signals.index_job, signals.create_admin_token]

    actions = signals.find_actions(Job, 'delete')
    assert actions == []


def test_on_models_committed_no_actions(monkeypatch, app):
    from jobber.core import signals

    mock = MagicMock()
    monkeypatch.setattr(signals, 'index_job', mock)

    company = Company(name='foocorp')
    changes = [(company, 'insert')]

    signals.on_models_committed(app, changes)

    assert not mock.called


def test_on_models_committed_job_model_not_published(monkeypatch, job, app):
    from jobber.core import signals

    mock_index = MagicMock(signals.Index)
    monkeypatch.setattr('jobber.core.signals.Index', mock_index)

    mock_create_admin_token = MagicMock()
    monkeypatch.setattr('jobber.core.signals.create_admin_token',
                        mock_create_admin_token)


    changes = [(job, 'insert')]
    signals.on_models_committed(app, changes)

    instance = mock_index.return_value
    assert not instance.add_document.called

    assert mock_create_admin_token.called


def test_on_models_committed_job_model_published(monkeypatch, job, app):
    from jobber.core import signals

    mock_index = MagicMock(signals.Index)
    monkeypatch.setattr('jobber.core.signals.Index', mock_index)

    mock_create_admin_token = MagicMock()
    monkeypatch.setattr('jobber.core.signals.create_admin_token',
                        mock_create_admin_token)

    job.published = True
    changes = [(job, 'insert')]
    signals.on_models_committed(app, changes)

    instance = mock_index.return_value
    assert instance.add_document.called

    assert mock_create_admin_token.called

