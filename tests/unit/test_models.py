# -*- coding: utf-8 -*-
"""
tests.unit.test_models
~~~~~~~~~~~~~~~~~~~~~~

Tests the model layer.

"""
import pytest
from unicodedata import normalize

from sqlalchemy.exc import IntegrityError

from jobber.core.utils import now
from jobber.models import (Job,
                           Company,
                           Category,
                           Location)


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


def test_company_model(company, session):
    name = u'remedica'
    assert company.id > 0
    assert company.name == name
    assert company.website is None
    assert company.slug == normalize('NFKD', name)
    assert company.created <= now()


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


def test_duplicate_company(session):
    company = Company(name='foobar')
    session.add(company)
    session.flush()

    with pytest.raises(IntegrityError):
        company = Company(name='foobar')
        session.add(company)
        session.flush()


def test_location_model(location, session):
    assert location.id > 0
    assert location.city == u'Lïｍáｓѕ߀ɭ'
    assert location.country_name == 'Cyprus'
    assert location.country_code == 'CYP'


def test_location_model_country_code_validator():
    with pytest.raises(ValueError):
        Location(city='Limassol', country_code='GOT')


def test_job_model(company, location, session):
    title = u'ｒíｂëｙé'
    job = Job(title=title,
              description=title,
              contact_method=1,
              remote_work=False,
              company_id=company.id,
              location_id=location.id,
              job_type=1)

    session.add(job)
    session.flush()

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
    assert job.url == u"{}/{}/{}".format(job.id, job.company.slug, job.slug)
    assert job.admin_url == u"{}/{}".format(job.id, job.admin_token)
    assert job.created <= now()


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
                  company_id=company.id,
                  location_id=location.id,
                  job_type=1)
        session.add(job)
        session.flush()
        assert job.id > 0
        assert job.title == title


def test_job_model_job_type_mapping(session):
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
            remote_work='', company_id=0, job_type=10)


def test_job_model_contact_method_mapping(session):
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

    category = Category(name=name, slug='forced')
    assert category.name == name
    assert category.slug == 'forced'
    assert category.created <= now()

    session.add(category)
    session.flush()
    assert category.id > 0
    assert category.name == name
    assert category.created <= now()


def test_duplicate_category(session):
    category = Category(name='foobar')
    session.add(category)
    session.flush()

    with pytest.raises(IntegrityError):
        category = Category(name='foobar')
        session.add(category)
        session.flush()
