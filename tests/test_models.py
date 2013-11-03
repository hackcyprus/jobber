# -*- coding: utf-8 -*-
"""
tests.test_models
~~~~~~~~~~~~~~~~~

Tests the model layer.

"""
import pytest
from jobber.models import Job, Company, Category



def test_company_model(session):
    name = u'٩(͡๏̯͡๏)۶ ٩(-̮̮̃•̃).'
    company = Company(name=name)
    session.add(company)
    session.flush()
    assert company.id > 0
    assert company.name == name
    assert company.about is None


def test_job_model(session):
    name = u'Båｃòｎ'
    company = Company(name=name)
    session.add(company)
    session.flush()
    assert company.id > 0

    title = u'ｒíｂëｙé'
    job = Job(title=title,
              description=title,
              how_to_apply=title,
              remote_work=False,
              company_id=company.id,
              job_type=1)
    session.add(job)
    session.flush()
    assert job.id > 0
    assert job.company_id == job.id
    assert job.title == title
    assert job.description == title
    assert job.how_to_apply == title


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

    category = Category(name=name, slug='forced')
    assert category.name == name
    assert category.slug == 'forced'

    session.add(category)
    session.flush()
    assert category.id > 0
    assert category.name == name
