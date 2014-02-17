"""
jobber.core.functions
~~~~~~~~~~~~~~~~~~~~~

Shared functions.

"""
import os
import uuid
from datetime import timedelta

from flask import current_app as app

from jobber.conf import settings
from jobber.core.email import send_email_template
from jobber.core.utils import now


DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER
ADMIN_RECIPIENT = settings.MAIL_ADMIN_RECIPIENT


def insert_token(email, token=None):
    """Inserts a unique token into the admin recipient address.

    :param nonce: A string to attach to the local part of the email. If not
    defined, one will be created randomly.

    """
    localpart, domain = email.split('@')
    if not token:
        token = uuid.uuid4().hex[:10]
    return '@'.join(['{}+{}'.format(localpart, token), domain])


def send_instructory_email(job):
    """Sends an email to the recruiter with instruction on how to do things.

    :param job: A `Job` instance.

    """
    recipient = job.recruiter_email
    context = {
        'job': job,
        'default_sender': DEFAULT_SENDER
    }
    app.logger.info(u"Sending instructory email to '{}' "
                    "for job listing ({}).".format(recipient, job.id))
    send_email_template('instructory', context, [recipient])


def send_admin_review_email(job, token=None):
    """Sends a notification to the admin to review the new/updated job listing.

    :param job: A `Job` instance.
    :param token: A string (of length 10) to attach to the reviewer email.

    """
    if token:
        token = token[:10]

    recipient = insert_token(settings.MAIL_ADMIN_RECIPIENT, token=token)

    probable_update = job.created + timedelta(minutes=5) < now()
    new_or_update = 'newly updated' if probable_update else 'brand new'

    # Some copy-paste convenience in the email...
    script_path = os.path.join(settings.ROOT, 'scripts', 'management')

    context = {
        'job': job,
        'new_or_update': new_or_update,
        'script_path': script_path
    }

    app.logger.info(u"Sending admin review email for job listing ({}).".format(job.id))
    send_email_template('review', context, [recipient])


def send_confirmation_email(job):
    """Sends an email to the recruiter, confirming that the job has been reviewed,
    accepted and published.

    :param job: A `Job` instance.

    """
    recipient = job.recruiter_email
    context = {
        'job': job,
        'default_sender': DEFAULT_SENDER
    }
    app.logger.info(u"Sending confirmation email to '{}' "
                    "for job listing ({}).".format(recipient, job.id))
    send_email_template('confirmation', context, [recipient])

