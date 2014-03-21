"""
Broadcasts a job to the selected social services.

Usage:
    broadcast.py <jobid> [<services> ...]

Options:
    <jobid>  The job to broadcast.
    <services> Optional space-separated list of services to broadcast to.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, die, green
from jobber.core.models import Job
from jobber.functions import social_broadcast, InvalidService


def main(jobid, services, session):
    job = session.query(Job).get(jobid)
    if not job:
        die("Job ({}) was not found.".format(jobid))
    try:
        social_broadcast(job, services=services)
        print green("Great, broadcasting to all services was successful.".format(', '.join(services)))
    except InvalidService as ise:
        die(ise)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    jobid = arguments['<jobid>']
    services = arguments['<services>']
    run(main, jobid, services)