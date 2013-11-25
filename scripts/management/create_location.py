"""
Creates a new location.

Usage:
    create_location.py <city> <country>

Options:
    <city>  The city.
    <country_code>  Alpha-3 country code.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green
from jobber.models import Location


def main(city, country_code, session):
    location = Location(city=city, country_code=country_code)
    session.add(location)


if __name__ == '__main__':
    arguments = docopt(__doc__)
    city = arguments['<city>']
    country = arguments['<country>']
    run(main, city, country)