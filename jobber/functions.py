"""
jobber.core.functions
~~~~~~~~~~~~~~~~~~~~~

Shared functions.

"""
import os
import logging
import json
from datetime import timedelta

import requests

from jobber.conf import settings
from jobber.core.email import send_email_template
from jobber.core.utils import now
from jobber.vendor.html2text import html2text


DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER
ADMIN_RECIPIENT = settings.MAIL_ADMIN_RECIPIENT
ZAPIER_WEBHOOK_URL = settings.ZAPIER_WEBHOOK_URL
DEFAULT_SOCIAL_SERVICES = settings.DEFAULT_SOCIAL_SERVICES


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


def social_broadcast(job, services=None):
    if services is None:
        services = DEFAULT_SOCIAL_SERVICES

    for service in services:
        sb = SocialBroadcast.make(service)
        try:
            sb.broadcast(job)
            logger.debug('Broadcast to {} for job ({}).'.format(service, job.id))
        except Exception as exc:
            # Let's not bail here. Catch all exceptions and log to make sure
            # we try the next service in line.
            msg = 'Failed broadcast to {} for job ({})!'.format(service, job.id)
            logger.exception(msg, exc)


class SocialBroadcast(object):
    """Factory class for creating `SocialBroadcast` objects based on the
    requested service.

    """

    @classmethod
    def make(cls, service):
        # We only support Twitter for now so this method ignores `service`.
        if service == 'twitter':
            return _Twitter()
        raise ValueError("Unknown social service '{}'".format(service))

    def broadcast(self, job):
        raise NotImplemented('Not implemented in factory class')


class _Twitter(SocialBroadcast):

    def broadcast(self, job):
        headers = {
            'Content-Type': 'application/json'
        }

        company = job.company
        location = job.location

        data = {
            'company': company.name,
            'title': job.title,
            'city': location.city,
            'country': location.country_name,
            'url': job.url(external=True)
        }

        data = json.dumps(data)
        r = requests.post(ZAPIER_WEBHOOK_URL, data=data, headers=headers)
        r.raise_for_status()
