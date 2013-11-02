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

from jobber.script import context, green
from jobber.extensions import db
from jobber.models import Company


def main(name):
    company = Company(name=name)
    db.session.add(company)
    db.session.commit()
    print green("'{}' created okay with id {}.".format(name, company.id))


if __name__ == '__main__':
    with context():
        arguments = docopt(__doc__)
        name = arguments['<name>']
        main(name)