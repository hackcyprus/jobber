# -*- coding: utf-8 -*-
"""
tests.unit.test_rss
~~~~~~~~~~~~~~~~~~~

Tests the RSS generation logic.

"""
import pytest
from jobber.core.models import Job, Company, Location
from jobber import rss


@pytest.fixture(scope='function')
def location():
    return Location(city=u'Limassol', country_code='CYP')


@pytest.fixture(scope='function')
def company():
    return Company(name=u'remedica')


@pytest.fixture(scope='function')
def job(company, location):
    return Job(title='testfoo',
               description='testfoo',
               contact_method=1,
               remote_work=False,
               company=company,
               location=location,
               job_type=1,
               recruiter_name=u'jon',
               recruiter_email=u'doe')


def test_rss_generation(job, session):
    session.add(job)
    session.commit()

    assert job.id > 0

    feed = rss.render_feed()

    # Assert on some generic information that needs to be present in the feed.
    url = job.url(external=True)
    location = u"{}, {}".format(job.location.city, job.location.country_name)
    title = u"{} at {} in {}".format(job.title, job.company.name, location)
    description = job.description

    assert url in feed
    assert title in feed
    assert description in feed
