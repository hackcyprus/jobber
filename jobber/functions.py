"""
jobber.core.functions
~~~~~~~~~~~~~~~~~~~~~

Email functionality using core email.

"""
import os
from datetime import timedelta

from flask import current_app as app

from jobber.conf import settings
from jobber.core.email import send_email_template
from jobber.core.utils import now


DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER


def send_instructory_email(job):
    """Sends an email to the recruiter with instruction on how to do things.

    :param job: A `Job` instance.

    """
    recipient = job.recruiter_email
    context = {
        'job': job,
        'default_sender': DEFAULT_SENDER
    }
    app.logger.debug("Sending instructory email to '{}'.".format(recipient))
    send_email_template('instructory', context, [recipient])


def send_admin_review_email(job):
    """Sends a notification to the admin to review the new/updated job post.

    :param job: A `Job` instance.

    """
    # We only wish to contact the admin if the job is not published hence it needs
    # review. Otherwise, even if the change was to publish the job, the admin would
    # have received an email.
    if job.published:
        return

    recipient = settings.MAIL_ADMIN_RECIPIENT

    probable_update = job.created + timedelta(minutes=5) < now()
    new_or_update = 'newly updated' if probable_update else 'brand new'

    # Some copy-paste convenience in the email...
    script_path = os.path.join(settings.ROOT, 'scripts', 'management')

    context = {
        'job': job,
        'new_or_update': new_or_update,
        'script_path': script_path
    }

    app.logger.debug("Sending admin review email for job ({}).".format(job.id))
    send_email_template('review', context, [recipient])
