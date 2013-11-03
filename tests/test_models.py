# -*- coding: utf-8 -*-
"""
tests.test_models
~~~~~~~~~~~~~~~~~

Tests the model layer.

"""
import pytest
from unicodedata import normalize

from jobber.models import Job, Company, Category, Location
from jobber.utils import now


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

    city = u'Lïｍáｓѕ߀ɭ'
    country = u'Cϒｐｒúｓ'
    location = Location(city=city, country=country)
    session.add(location)

    session.flush()

    title = u'ｒíｂëｙé'
    job = Job(title=title,
              description=title,
              how_to_apply=title,
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
    assert job.how_to_apply == title
    assert job.slug == normalize('NFKD', title)
    assert job.created <= now()


def test_job_model_job_type_helpers(session):
    assert Job.machinize_job_type('full_time') == 1
    with pytest.raises(KeyError):
        Job.machinize_job_type('wat?')

    assert Job.humanize_job_type(1) == 'full_time'
    with pytest.raises(KeyError):
        Job.humanize_job_type(5)


def test_job_model_job_type_validator():
    with pytest.raises(ValueError):
        Job(title='', description='', how_to_apply='',
            remote_work='', company_id=0, job_type=10)


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
    country = u'Cϒｐｒúｓ'
    location = Location(city=city, country=country)
    session.add(location)
    session.flush()
    assert location.id > 0
    assert location.city == city
    assert location.country == country
