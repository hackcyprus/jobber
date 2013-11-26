"""
jobber.view_helpers
~~~~~~~~~~~~~~~~~~~

Utility functions for views.

"""
from jobber.models import Job, Company, Location
from jobber.core.forms import JobForm
from jobber.extensions import db


def populate_form(job):
    """Populates a `JobForm` object from a `Job` model.

    :param job: A `Job` instance.

    """
    location = job.location
    company = job.company

    related_data = {
        'location__id': location.id,
        'location__city': location.city,
        'location__country_code': location.country_code,
        'company__id': company.id,
        'company__name': company.name,
        'company__website': company.website
    }

    return JobForm(obj=job, **related_data)


def populate_company(job, form_data):
    """Populates the company relation from `job` and `form_data`.

    :param job: A `Job` instance.
    :param form_data: Form data as a `dict`.

    """
    company = None
    company_id = form_data['company__id']

    if job.company_id is not None and (job.company_id == company_id):
        return

    if company_id:
        company = Company.query.get(company_id)

    if not company:
        name = form_data['company__name']
        website = form_data.get('company__website')
        company = Company(name=name, website=website)
        db.session.add(company)

    job.company = company


def populate_location(job, form_data):
    """Populates the location relation form `job` and `form_data`.

    :param job: A `Job` instance.
    :param form_data: Form data as a `dict`.

    """
    location = None
    location_id = form_data['location__id']

    if job.location_id is not None and (job.location_id == location_id):
        return

    if location_id:
        location = Location.query.get(location_id)

    if not location:
        city = form_data['location__city']
        country_code = form_data['location__country_code']
        location = Location(city=city, country_code=country_code)
        db.session.add(location)

    job.location = location


def populate_job(form, job=None):
    """Populates a `Job` model from a `JobForm` object.

    :param form: A `JobForm` instance.

    """
    if job is None:
        job = Job()
        db.session.add(job)

    form_data = form.data

    job.title = form_data['title']
    job.description = form_data['description']
    job.job_type = form_data['job_type']
    job.contact_method = form_data['contact_method']
    job.remote_work = form_data['remote_work']

    if job.contact_method == 1:
        job.contact_url = form_data['contact_url']
    else:
        job.contact_email = form_data['contact_email']

    job.populate_slug()

    populate_company(job, form_data)
    populate_location(job, form_data)

    return job