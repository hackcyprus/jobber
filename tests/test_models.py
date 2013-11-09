# -*- coding: utf-8 -*-
"""
tests.test_models
~~~~~~~~~~~~~~~~~

Tests the model layer.

"""
import pytest
from unicodedata import normalize

from jobber.models import Job, Company, Category, Location
from jobber.core.utils import now


def test_company_model(session):
    name = u'٩(͡๏̯͡๏)۶ ٩(-̮̮̃•̃).'
    company = Company(name=name)
    session.add(company)
    session.flush()
    assert company.id > 0
    assert company.name == name
    assert company.about is None
    assert company.created <= now()


def test_job_model(session):
    name = u'Båｃòｎ'
    company = Company(name=name)
    session.add(company)

    location = Location(city=u'Lïｍáｓѕ߀ɭ', country_code='CYP')
    session.add(location)

    session.flush()

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
    assert job.company_id == company.id
    assert job.company.id == company.id
    assert job.location_id == location.id
    assert job.location.id == location.id
    assert job.title == title
    assert job.description == title
    assert job.contact_method == 1
    assert job.job_type == 1
    assert job.slug == normalize('NFKD', title)
    assert job.created <= now()


def test_job_model_job_type_helpers(session):
    assert Job.machinize_job_type('Full Time') == 1
    with pytest.raises(KeyError):
        Job.machinize_job_type('wat?')

    assert Job.humanize_job_type(1) == 'Full Time'
    with pytest.raises(KeyError):
        Job.humanize_job_type(5)


def test_job_model_job_type_validator():
    with pytest.raises(ValueError):
        Job(title='', description='', contact_method=1,
            remote_work='', company_id=0, job_type=10)


def test_job_model_contact_method_helpers(session):
    assert Job.machinize_contact_method('url') == 1
    with pytest.raises(KeyError):
        Job.machinize_job_type('wat?')

    assert Job.humanize_contact_method(1) == 'url'
    with pytest.raises(KeyError):
        Job.humanize_job_type(5)


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


def test_location_model(session):
    city = u'Lïｍáｓѕ߀ɭ'
    code = 'CYP'
    location = Location(city=city, country_code=code)
    session.add(location)
    session.flush()
    assert location.id > 0
    assert location.city == city
    assert location.country_name == 'Cyprus'
    assert location.country_code == code


def test_location_model_country_code_validator():
    with pytest.raises(ValueError):
        Location(city='Limassol', country_code='GOT')
