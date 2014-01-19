# -*- coding: utf-8 -*-
"""
tests.unit.test_models
~~~~~~~~~~~~~~~~~~~~~~

Tests the model layer.

"""
import pytest
from unicodedata import normalize

from sqlalchemy.exc import IntegrityError
from arrow.arrow import Arrow

from jobber.core.utils import now
from jobber.core.models import (Job,
                           Company,
                           Category,
                           Location,
                           Tag)


@pytest.fixture(scope='function')
def location():
    return Location(city=u'Lïｍáｓѕ߀ɭ', country_code='CYP')


@pytest.fixture(scope='function')
def company():
    return Company(name=u'remedica')


def test_company_model(company, session):
    # Commit session for `company` fixture to be persisted.
    session.add(company)
    session.commit()

    name = u'remedica'
    assert company.id > 0
    assert company.website is None
    assert company.slug == normalize('NFKD', name)
    assert company.created <= now()

    # Check if we get `arrow` dates back.
    assert type(company.created) is Arrow


def test_company_slug_model_mixin():
    company = Company()
    assert company.slug is None

    company.populate_slug()
    assert company.slug is None

    company.name = u'test'
    company.populate_slug()
    assert company.slug == u'test'

    company.name = u'test1'
    company.populate_slug()
    assert company.slug == u'test1'


def test_duplicate_company_is_allowed(session):
    company = Company(name='foobar')
    session.add(company)
    session.commit()

    company = Company(name='foobar')
    session.add(company)
    session.commit()


def test_location_model(location, session):
    # Commit session for `location` fixture to be persisted.
    session.add(location)
    session.commit()

    assert location.id > 0
    assert location.city == u'Lïｍáｓѕ߀ɭ'
    assert location.country_name == 'Cyprus'
    assert location.country_code == 'CYP'
    assert location.created <= now()

    # Check if we get `arrow` dates back.
    assert type(location.created) is Arrow


def test_location_model_country_code_validator():
    with pytest.raises(ValueError):
        Location(city='Limassol', country_code='GOT')


def test_job_model(company, location, session):
    title = u'ｒíｂëｙé'
    recruiter_name = u'相'
    recruiter_email = u'思'

    job = Job(title=title,
              description=title,
              contact_method=1,
              remote_work=False,
              company=company,
              location=location,
              job_type=1,
              recruiter_name=recruiter_name,
              recruiter_email=recruiter_email)

    session.add(job)
    session.commit()

    assert job.id > 0
    assert not job.published
    assert job.company_id == company.id
    assert job.company.id == company.id
    assert job.location_id == location.id
    assert job.location.id == location.id
    assert job.title == title
    assert job.description == title
    assert job.contact_method == 1
    assert job.job_type == 1
    assert job.slug == normalize('NFKD', title)
    assert str(job.id) in job.url()
    assert job.company.slug in job.url()
    assert 'http' not in job.url()
    assert str(job.id) in job.url(external=True)
    assert job.company.slug in job.url(external=True)
    assert 'http' in job.url(external=True)
    assert str(job.id) in job.edit_url() and job.admin_token in job.edit_url()
    assert job.recruiter_name == recruiter_name
    assert job.recruiter_email == recruiter_email
    assert job.created <= now()

    # Check if we get `arrow` dates back.
    assert type(job.created) is Arrow


def test_job_slug_model_mixin():
    job = Job()
    assert job.slug is None

    job.populate_slug()
    assert job.slug is None

    job.title = u'test'
    job.populate_slug()
    assert job.slug == u'test'

    job.title = u'test1'
    job.populate_slug()
    assert job.slug == u'test1'


def test_duplicate_job_model(company, location, session):
    title = u'foobar'

    for _ in range(3):
        job = Job(title=title,
                  description=title,
                  contact_method=1,
                  remote_work=False,
                  company=company,
                  location=location,
                  job_type=1,
                  recruiter_name=u'Αλέκος',
                  recruiter_email=u'alekos@Κόκοτας.com')

        session.add(job)
        session.commit()

        assert job.id > 0
        assert job.title == title


def test_job_model_job_type_mapping():
    job_types = Job.JOB_TYPES

    assert job_types.inverse('Full Time') == 1
    with pytest.raises(KeyError):
        job_types.inverse('wat?')

    assert job_types.map(1) == 'Full Time'
    with pytest.raises(KeyError):
        job_types.map(5)


def test_job_model_job_type_validator():
    with pytest.raises(ValueError):
        Job(title='', description='', contact_method=1,
            remote_work='', company_id=0, job_type=10,
            recruiter_name='a', recruiter_email='a')


def test_job_model_contact_method_mapping():
    contact_methods = Job.CONTACT_METHODS

    assert contact_methods.inverse('Link') == 1
    with pytest.raises(KeyError):
        contact_methods.inverse('wat?')

    assert contact_methods.map(1) == 'Link'
    with pytest.raises(KeyError):
        contact_methods.map(5)


def test_job_model_contact_method_validator():
    with pytest.raises(ValueError):
        Job(title='', description='', contact_method=10,
            remote_work='', company_id=0, job_type=1)


def test_category_model(session):
    name = u'foo bar'
    category = Category(name=name)
    assert category.name == name
    assert category.slug == u'foo-bar'
    assert category.created <= now()

    category = Category(name=name, slug=u'forced')
    assert category.name == name
    assert category.slug == u'forced'
    assert category.created <= now()

    session.add(category)
    session.commit()

    assert category.id > 0
    assert category.name == name
    assert category.created <= now()


def test_duplicate_category(session):
    category = Category(name=u'foobar')
    session.add(category)
    session.commit()

    with pytest.raises(IntegrityError):
        category = Category(name=u'foobar')
        session.add(category)
        session.commit()


def test_tag_model(session):
    tag_name = u'foo bar'
    tag = Tag(tag=tag_name)

    session.add(tag)
    session.commit()

    assert tag.tag == tag_name
    assert tag.slug == u'foo-bar'
    assert tag.created <= now()


def test_duplicate_tag(session):
    tag = Tag(tag=u'dup')
    session.add(tag)
    session.commit()

    with pytest.raises(IntegrityError):
        tag = Tag(tag=u'dup')
        session.add(tag)
        session.commit()


def test_adding_tag(session, company, location):
    one = Tag(tag=u'one')

    # Test adding tags via the constructor.
    job = Job(title=u'foo',
              description=u'foo',
              contact_method=1,
              remote_work=False,
              company=company,
              location=location,
              job_type=1,
              recruiter_name=u'foo bar',
              recruiter_email=u'foo@fooland.com',
              tags=[one])

    # Try to add one existing and two new tags.
    tags = job.add_tags([u'one', u'two', u'three'])

    session.add(job)
    session.commit()

    assert len(job.tags) == 3
    for tag in tags:
        assert tag in job.tags


def test_replacing_tag(session, company, location):
    one = Tag(tag=u'one')
    two = Tag(tag=u'two')

    # Test adding tags via the constructor.
    job = Job(title=u'foo',
              description=u'foo',
              contact_method=1,
              remote_work=False,
              company=company,
              location=location,
              job_type=1,
              recruiter_name=u'foo bar',
              recruiter_email=u'foo@fooland.com',
              tags=[one, two])

    job.replace_tags([u'three'])

    session.add(job)
    session.commit()

    assert len(job.tags) == 1
    assert one not in job.tags
    assert two not in job.tags
