"""
Searches the `jobs` index.

Usage:
    search_index.py <query>

Options:
    <query>  Query to search for.

"""
import time
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, die
from jobber.models import Job
from jobber.core.search import Index


def main(query, session):
    if not Index.exists():
        die('Search index does not exist!')

    if isinstance(query, str):
        query = unicode(query, 'utf-8')

    index = Index()
    for result in index.search(query):
        job = Job.query.get(result['id'])
        print job


if __name__ == '__main__':
    arguments = docopt(__doc__)
    query = arguments['<query>']
    run(main, query)
