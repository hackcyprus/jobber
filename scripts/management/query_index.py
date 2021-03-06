"""
Searches the `jobs` index.

Usage:
    query_index.py <query>

Options:
    <query>  Query to search for.

"""
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, die
from jobber.core.models import Job
from jobber.core.search import IndexManager, Index
from jobber.conf import settings


def main(query, session):
    name = settings.SEARCH_INDEX_NAME
    directory = settings.SEARCH_INDEX_DIRECTORY

    if not IndexManager.exists(name, directory):
        die('Search index does not exist!')

    if isinstance(query, str):
        query = unicode(query, 'utf-8')

    index = Index()
    for result in index.search(query):
        job = session.query(Job).get(result['id'])
        print job


if __name__ == '__main__':
    arguments = docopt(__doc__)
    query = arguments['<query>']
    run(main, query)
