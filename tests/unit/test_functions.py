# -*- coding: utf-8 -*-
"""
tests.unit.test_functions
~~~~~~~~~~~~~~~~~~~~~~~~~

Tests shared functions.

"""
import os

import pytest
from mock import MagicMock

from jobber.conf import settings
from jobber.core.models import Location, Company, Job
from jobber.functions import (send_instructory_email,
                              send_admin_review_email,
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
        'script_path': os.path.join(settings.ROOT, 'scripts', 'management')
    }
    recipient = [ADMIN_RECIPIENT]

    send_admin_review_email(job)
    mock.assert_called_with('review', context, recipient)
