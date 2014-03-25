"""
Broadcasts jobs to social networks. On every script run, a job will be selected
for broadcasting according to the following rules:

(job is published) AND (
    (job not broadcasted before) OR (job last broadcasted successfully >= N days ago)
)

Usage:
    broadcast.py

"""
import logging

from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run
from jobber.core.models import Job, SocialBroadcast
from jobber.core.utils import now
from jobber.conf import settings
from jobber.functions import social_broadcast


logger = logging.getLogger('jobber')


def main(session):
    logger.info('Selecting candidates for broadcast.')

    threshold = settings.BROADCAST_EXPIRY_THRESHOLD_DAYS
    services = settings.ZAPIER_WEBHOOKS.keys()

    selection = []

    for job in session.query(Job).filter_by(published=True):
        broadcasts = session.query(SocialBroadcast)\
                     .filter_by(job=job, success=True)\
                     .order_by(SocialBroadcast.created.desc())\
                     .all()

        if not broadcasts:
            logger.debug(
                "Selecting job ({}) because it has not been "
                "broadcasted before.".format(job.id)
            )
            selection.append(job)
            continue

        diff = (now() - broadcasts[0].created).days
        if diff >= threshold:
            logger.debug(
                "Selecting job ({}) because it has not been "
                "successfully broadcasted for {} days.".format(job.id, threshold)
            )
            selection.append(job)
            continue

        logger.debug("Skipping job ({}) for broadcasting.".format(job.id))

    logger.info("Selected {} candidates for broadcast.".format(len(selection)))

    for selected in selection:
        for service in services:
            sb = social_broadcast(selected, service)
            session.add(sb)
            session.commit()


if __name__ == '__main__':
    arguments = docopt(__doc__)
    run(main)
