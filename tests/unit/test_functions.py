# -*- coding: utf-8 -*-
"""
tests.unit.test_functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Tests shared functions.

"""
import os
import re

import pytest
from mock import MagicMock

from jobber.conf import settings
from jobber.core.models import Location, Company, Job
from jobber.functions import (send_instructory_email,
                              send_admin_review_email,
                              send_confirmation_email,
                              insert_token,
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


def test_insert_token():
    recipient = 'bob@example.com'

    nonced = insert_token(recipient)

    assert 'bob+' in nonced
    assert re.match('.*[a-z0-9]{10}.*', nonced) is not None

    nonced = insert_token(recipient, token='foofoofoo')
    assert 'bob+foofoofoo' in nonced


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
        'script_path': os.path.join(settings.ROOT, 'scripts', 'management')
    }

    token = 'foo'
    recipient = [insert_token(ADMIN_RECIPIENT, token=token)]

    send_admin_review_email(job, token=token)
    mock.assert_called_with('review', context, recipient)


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
