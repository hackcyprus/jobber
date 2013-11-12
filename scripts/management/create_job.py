"""
Creates a new job interactively.

A company and a location *need to exist* before the job is created.

Usage:
    create_job.py

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green, die, prompt
from jobber.models import Company, Job, Location


def handle_location(id):
    location = Location.query.get(id)
    if location is None:
        die("Location {} does not exist! Bye.".format(id))
    return location


def handle_company(id):
    company = Company.query.get(id)
    if company is None:
        die("Company {} does not exist! Bye.".format(id))
    return company


def handle_job_type(value):
    return Job.JOB_TYPES.inverse(value)


def handle_contact_method(value):
    return Job.CONTACT_METHODS.inverse(value)


def handle_remote_work(value):
    return Job.REMOTE_WORK_OPTIONS.inverse(value)


def pick_contact_field(value):
    if value == 1:
        return 'contact_url'
    elif value == 2:
        return 'contact_email'


field_schema = {
    'title': {
        'prompt': "What's the title of this job?",
        'next': 'location'
    },
    'location': {
        'prompt': "What's the location of this job?",
        'handler': handle_location,
        'next': 'company'
    },
    'company': {
        'prompt': 'Which company is posting the job?',
        'handler': handle_company,
        'next': 'job_type'
    },
    'job_type': {
        'prompt': 'What type of job is it?',
        'handler': handle_job_type,
        'next': 'remote_work'
    },
    'remote_work': {
        'prompt': 'Can people work remotely?',
        'handler': handle_remote_work,
        'next': 'contact_method'
    },
    'contact_method': {
        'prompt': 'How can someone apply to this job?',
        'handler': handle_contact_method,
        'next': pick_contact_field
    },
    'contact_url': {
        'name': 'contact_url',
        'prompt': "Okay, what's the url?"
    },
    'contact_email': {
        'name': 'contact_email',
        'prompt': "Okay, what's the email?"
    }
}

def main(session):
    kwargs = dict()
    next = 'title'

    while next:
        field = field_schema[next]
        message = field['prompt']
        handler = field.get('handler')
        value = prompt(message)
        if handler:
            value = handler(value)
        kwargs[next] = value
        next = field.get('next')
        if hasattr(next, '__call__'):
            next = next(value)

    job = Job(**kwargs)
    session.add(job)
    session.flush()

    print green("'{}' created okay with id {}.".format(job.title, job.id))


if __name__ == '__main__':
    docopt(__doc__)
    run(main)
