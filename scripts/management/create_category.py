"""
Creates a new category.

Usage:
    create_category.py <name>

Options:
    <name>  The name of the category.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green
from jobber.models import Category


def main(name, session):
    category = Category(name=name)
    session.add(category)
    session.flush()
    msg = "Category '{}' (slug: '{}') created okay with id {}."
    print green(msg.format(name, category.slug, category.id))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    name = arguments['<name>']
    run(main, name)