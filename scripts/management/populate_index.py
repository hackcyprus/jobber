"""
Populates the `jobs` index. So far we've got only one index so this script
knows how to do one thing well.

Usage:
    populate_index.py [--create] [--published]

Options:
    --create     Whether the index should be re-created.
    --published  Index only published jobs.

"""
import time
from docopt import docopt

from env import path_setup
path_setup()

from jobber.script import run, green, die, blue
from jobber.core.models import Job
from jobber.core.search import Index, Schema


def main(should_create, only_published, session, app):
    if should_create:
        print blue("You've asked to (re)create index '{}'.".format(Index.name))
        schema = Schema()
        Index.create(schema)

    if not Index.exists():
        die('Search index does not exist!')

    index = Index()

    start = time.time()
    jobs = [
        job.to_document() for job in session.query(Job).all()
        if (not only_published) or (only_published and job.published)
    ]

    index.add_document_bulk(jobs)
    duration = time.time() - start

    print green("{0} documents added okay in {1:.2f} ms.".format(len(jobs), duration))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    should_create = arguments['--create']
    only_published = arguments['--published']
    run(main, should_create, only_published)
