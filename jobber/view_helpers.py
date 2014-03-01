"""
jobber.view_helpers
~~~~~~~~~~~~~~~~~~~

Utility functions for views.

"""
from jobber.core.models import Job, Company, Location, Tag
from jobber.core.forms import JobForm
from jobber.core.utils import insert_email_token
from jobber.functions import send_admin_review_email
from jobber.conf import settings
from jobber.database import db


REVIEWER_ROBOT = settings.MAIL_REVIEWER_ROBOT


def get_location_context():
    """Returns location data for the create/edit form."""
    return [
        dict(id=location.id, city=location.city, country_code=location.country_code)
        for location in db.session.query(Location).all()
    ]


def get_tag_context():
    """Returns tags data for the create/edit form."""
    return [
        dict(slug=tag.slug, tag=tag.tag) for tag in db.session.query(Tag).all()
    ]


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
        'company__website': company.website_with_protocol
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
        company = db.session.query(Company).get(company_id)

    if not company:
        name = form_data['company__name']
        website = form_data.get('company__website')
        company = Company(name=name, website=website)

    job.company = company


def populate_location(job, form_data):
    """Populates the location relation from `job` and `form_data`.

    :param job: A `Job` instance.
    :param form_data: Form data as a `dict`.

    """
    location = None
    location_id = form_data['location__id']

    if job.location_id is not None and (job.location_id == location_id):
        return

    if location_id:
        location = db.session.query(Location).get(location_id)

    if not location:
        city = form_data['location__city']
        country_code = form_data['location__country_code']
        location = Location(city=city, country_code=country_code)

    job.location = location


def populate_job(form, job=None):
    """Populates a `Job` model from a `JobForm` object.

    :param form: A `JobForm` instance.

    """
    if job is None:
        job = Job()

    form_data = form.data

    job.title = form_data['title']
    job.description = form_data['description']
    job.job_type = form_data['job_type']
    job.contact_method = form_data['contact_method']
    job.remote_work = form_data['remote_work']

    job.replace_tags(form_data['tags'])

    job.recruiter_name = form_data['recruiter_name']
    job.recruiter_email = form_data['recruiter_email']

    job.populate_slug()

    if job.contact_method == 1:
        job.contact_url = form_data['contact_url']
    else:
        job.contact_email = form_data['contact_email']

    populate_company(job, form_data)
    populate_location(job, form_data)

    return job


def send_review_email(job, token):
    """Sends an admin review email using the given `token`.

    :param token: A string of length 10 to use as the review token.

    """
    sender = insert_email_token(REVIEWER_ROBOT, token=token)
    send_admin_review_email(job, sender=sender)
