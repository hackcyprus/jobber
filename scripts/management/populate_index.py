"""
Populates the `jobs` index. So far we've got only one index so this script
knows how to do one thing well.

Usage:
    populate_index.py [--create] [--all]

Options:
    --create     Whether the index should be re-created.
    --all        Index all jobs. By default, only published jobs will be indexed.

"""
import time
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green, die, blue
from jobber.core.models import Job
from jobber.core.search import IndexManager, Schema, Index
from jobber.conf import settings


def main(should_create, index_all, session):
    name = settings.SEARCH_INDEX_NAME
    directory = settings.SEARCH_INDEX_DIRECTORY

    if should_create:
        print blue("You've asked to (re)create index '{}'.".format(name))
        IndexManager.create(Schema, name, directory)

    if not IndexManager.exists(name, directory):
        die('Search index does not exist!')

    index = Index()

    start = time.time()

    kwargs = {} if index_all else {'published': True}
    jobs = session.query(Job).filter_by(**kwargs).all()

    index.add_document_bulk([job.to_document() for job in jobs])
    duration = time.time() - start

    print green("{0} documents added okay in {1:.2f} ms.".format(len(jobs), duration))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    should_create = arguments['--create']
    index_all = arguments['--all']
    run(main, should_create, index_all)
