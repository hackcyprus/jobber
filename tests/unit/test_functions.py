# -*- coding: utf-8 -*-
"""
tests.unit.test_functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Tests shared functions.

"""
import os
import json

import pytest
import requests
from mock import MagicMock

from jobber.vendor.html2text import html2text
from jobber.conf import settings
from jobber.core.models import Location, Company, Job
from jobber.functions import (send_instructory_email,
                              send_admin_review_email,
                              send_confirmation_email,
                              social_broadcast,
                              Zapier,
                              DEFAULT_SENDER,
                              ADMIN_RECIPIENT)


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


def test_send_instructory_email(app, monkeypatch, job):
    mock = MagicMock()
    monkeypatch.setattr('jobber.functions.send_email_template', mock)

    context = {
        'job': job,
        'default_sender': DEFAULT_SENDER
    }
    recipient = [job.recruiter_email]

    send_instructory_email(job)
    mock.assert_called_with('instructory', context, recipient)


def test_send_admin_review_email(app, monkeypatch, job):
    mock = MagicMock()
    monkeypatch.setattr('jobber.functions.send_email_template', mock)

    context = {
        'job': job,
        'new_or_update': 'brand new',
        'script_path': os.path.join(settings.ROOT, 'scripts', 'management'),
        'html2text': html2text
    }

    sender= 'tech+reviewer+foo@projectcel.com'
    recipient = [ADMIN_RECIPIENT]

    send_admin_review_email(job, sender=sender)
    mock.assert_called_with('review', context, recipient, sender=sender)


def test_send_confirmation_email(app, monkeypatch, job):
    mock = MagicMock()
    monkeypatch.setattr('jobber.functions.send_email_template', mock)

    context = {
        'job': job,
        'default_sender': DEFAULT_SENDER
    }
    recipient = [job.recruiter_email]

    send_confirmation_email(job)
    mock.assert_called_with('confirmation', context, recipient)


def test_social_broadcast(session, monkeypatch, job):
    data = {
        'status': 'success',
        'foo': 'bar'
    }

    session.add(job)
    session.commit()

    mock = MagicMock()
    mock.return_value = data
    monkeypatch.setattr('jobber.functions.Zapier.broadcast', mock)

    sb = social_broadcast(job, 'twitter')

    assert sb.success
    assert sb.service == 'twitter'
    assert sb.data == json.dumps(data)
    assert sb.job_id == job.id


def test_social_broadcast_fail(session, monkeypatch, job):
    session.add(job)
    session.commit()

    mock = MagicMock()
    mock.side_effect = requests.HTTPError()
    monkeypatch.setattr('jobber.functions.Zapier.broadcast', mock)

    sb = social_broadcast(job, 'twitter')

    assert not sb.success
    assert sb.service == 'twitter'
    assert sb.data == json.dumps({})
    assert sb.job_id == job.id
