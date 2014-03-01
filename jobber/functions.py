"""
jobber.core.functions
~~~~~~~~~~~~~~~~~~~~~

Shared functions.

"""
import os
import logging
from datetime import timedelta

from jobber.conf import settings
from jobber.core.email import send_email_template
from jobber.core.utils import now
from jobber.vendor.html2text import html2text


DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER
ADMIN_RECIPIENT = settings.MAIL_ADMIN_RECIPIENT


logger = logging.getLogger('jobber')


def send_instructory_email(job):
    """Sends an email to the recruiter with instruction on how to do things.

    :param job: A `Job` instance.

    """
    recipient = job.recruiter_email
    context = {
        'job': job,
        'default_sender': DEFAULT_SENDER
    }
    logger.info(u"Sending instructory email to '{}' "
                    "for job listing ({}).".format(recipient, job.id))
    send_email_template('instructory', context, [recipient])


def send_admin_review_email(job, sender=None):
    """Sends a notification to the admin to review the new/updated job listing.

    :param job: A `Job` instance.
    :param sender: The A string (of length 10) to attach to the email sender.

    """
    recipient = settings.MAIL_ADMIN_RECIPIENT

    probable_update = job.created + timedelta(minutes=5) < now()
    new_or_update = 'newly updated' if probable_update else 'brand new'

    # Some copy-paste convenience in the email...
    script_path = os.path.join(settings.ROOT, 'scripts', 'management')

    context = {
        'job': job,
        'html2text': html2text,
        'new_or_update': new_or_update,
        'script_path': script_path
    }

    if sender is None:
        sender = DEFAULT_SENDER

    logger.info(u"Sending admin review email for job listing ({}).".format(job.id))
    send_email_template('review', context, [recipient], sender=sender)


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
    logger.info(u"Sending confirmation email to '{}' "
                    "for job listing ({}).".format(recipient, job.id))
    send_email_template('confirmation', context, [recipient])

