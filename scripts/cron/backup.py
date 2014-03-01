"""
Takes a backup of the database on Dropbox - hacking it all the way.

Usage:
    backup.py

"""
import logging

from docopt import docopt
from dropbox.client import DropboxClient
from dropbox.rest import ErrorResponse

from env import path_setup
path_setup()

from jobber.script import run
from jobber.core.utils import now
from jobber.conf import settings
from jobber.factory import create_app


app = create_app(__name__)
logger = logging.getLogger('jobber')


def main(session):
    dropbox = DropboxClient(settings.DROPBOX_OAUTH_TOKEN)

    dburi = settings.SQLALCHEMY_DATABASE_URI
    dbpath = dburi.replace('sqlite:////', '')

    env = 'production' if not settings.DEBUG else 'dev'
    filename = 'backup.{}.{}.db'.format(now().format('YYYYMMDDHHmm'), env)

    logger.info('Backup started for {} with filename {}.'.format(dbpath, filename))
    with open(dbpath) as db:
        try:
            response = dropbox.put_file(filename, db)
            rev = response['rev']
            logger.info("Backup complete with revision id {}.".format(rev))
        except ErrorResponse as err:
            code = err.status
            msg = err.error_msg
            logger.error("Backup failed with code {} message '{}'.".format(code, msg))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    run(main)
