"""
Broadcasts a job to the selected social services.

Usage:
    broadcast.py <jobid> <service>

Options:
    <jobid>    The job to broadcast.
    <service>  Service identifier.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, die, green
from jobber.core.models import Job
from jobber.functions import social_broadcast


def main(jobid, service, session):
    job = session.query(Job).get(jobid)
    if not job:
        die("Job ({}) was not found.".format(jobid))
    try:
        sb = social_broadcast(job, service)
        session.add(sb)
        session.commit()
        print green("Great, broadcasting was successful.")
    except Exception as exc:
        die(exc)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    jobid = arguments['<jobid>']
    service = arguments['<service>']
    run(main, jobid, service)