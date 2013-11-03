"""
Creates a new locatin.

Usage:
    create_location.py <city> <country>

Options:
    <city>  The city.
    <country>  The country.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green
from jobber.models import Location


def main(city, country, session):
    location = Location(city=city, country=country)
    session.add(location)
    session.flush()
    msg = "Location '{}, {}' created okay with id {}."
    print green(msg.format(city, country, location.id))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    city = arguments['<city>']
    country = arguments['<country>']
    run(main, city, country)