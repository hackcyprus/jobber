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
    return Job(title=u'testfoo',
               description=u'testfoo',
               contact_method=1,
               remote_work=False,
               company=company,
               location=location,
               published=True,
               job_type=1,
               recruiter_name=u'jon',
               recruiter_email=u'jon@doe.com')


@pytest.mark.parametrize("query", [None, u'testfoo'])
def test_rss_generation(session, signals, job, query):
    session.add(job)
    session.commit()

    assert job.id > 0

    feed = rss.render_feed(query=query)

    # Assert on some generic information that needs to be present in the feed.
    url = job.url(external=True)
    location = u"{}, {}".format(job.location.city, job.location.country_name)
    title = u"{} at {} in {}".format(job.title, job.company.name, location)
    description = job.description

    assert url in feed
    assert title in feed
    assert description in feed
