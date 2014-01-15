"""
Creates a new company.

Usage:
    create_company.py <name>

Options:
    <name>  The name of the company.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green
from jobber.core.models import Company


def main(name, session):
    company = Company(name=name)
    session.add(company)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    name = arguments['<name>']
    run(main, name)