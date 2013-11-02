"""
Creates a new job. A company needs to exist before the job is created.

Usage:
    create_job.py <title> <job_type> <company_id>

Options:
    <title>  The title of the job.
    <job_type>  Type of job, one of 'full_time', 'part_time', 'contract', 'internship'.
    <company_id>  The id of the company posting this job.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green, die
from jobber.models import Company, Job


def main(title, job_type, company_id, session):
    company = Company.query.get(company_id)
    if company is None:
        die("Company {} does not exist! Bye.".format(company_id))

    job_type = Job.machinize_job_type(job_type)

    job = Job(title=title, job_type=job_type, company=company)
    session.add(job)
    session.flush()
    print green("'{}' created okay with id {}.".format(title, job.id))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    title = arguments['<title>']
    job_type = arguments['<job_type>']
    company_id = int(arguments['<company_id>'])
    run(main, title, job_type, company_id)
