# -*- coding: utf-8 -*-
"""
Job review script.

Usage:
    review.py <job_id>

Options:
    <job_id>  The id of the job to review.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green, die, prompt, blue
from jobber.core.models import Job
from jobber.functions import send_confirmation_email
from jobber.vendor.html2text import html2text


def make_summary(job):
    summary = u"""
    Title: {title}

    Type: {job_type}
    Remote Work: {remote_work}

    Recruiter: {recruiter_name}
    Recruiter email: {recruiter_email}

    Company: {company_name}
    Company Website: {company_website}

    City: {city}
    Country Code: {country_code}

    Tags: {tags}

    Published: {published}

    Description
    -----------
    {description}

    => You can also view this listing online at {edit_url}.
    """
    return summary.format(**{
        'title': job.title,
        'job_type': job.human_job_type,
        'remote_work': job.human_remote_work,
        'description': html2text(job.description),
        'recruiter_name': job.recruiter_name,
        'recruiter_email': job.recruiter_email,
        'company_name': job.company.name,
        'company_website': job.company.website_with_protocol,
        'city': job.location.city,
        'country_code': job.location.country_code,
        'edit_url': job.edit_url(),
        'tags': u', '.join(job.tag_slugs),
        'published': job.published
    })


def main(job_id, session, app):
    job = session.query(Job).get(job_id)

    if not job:
        die("Job ({}) does not exist.".format(job_id))

    print isinstance(job.title, unicode)

    print "You're reviewing the following listing:"
    print make_summary(job).encode('utf-8')

    action = 'publish' if not job.published else 'unpublish'
    if prompt("Do you want to {} this listing?".format(blue(action)), yesno=True):
        job.published = not job.published
        session.commit()

        print green('Job {}ed!'.format(action))

        if action == 'unpublish':
            return

        if prompt(blue('Do you want to send a confirmation email?'), yesno=True):
            send_confirmation_email(job)
            print green('Confirmation email sent!')
    else:
        die('Bye.')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    job_id = int(arguments['<job_id>'])
    run(main, job_id)
