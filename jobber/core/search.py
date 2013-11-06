"""
jobber.core.search
~~~~~~~~~~~~~~~~~~

Handles all things search.

"""
from contextlib import contextmanager

from whoosh.fields import SchemaClass, TEXT
from whoosh import index
from whoosh.writing import IndexingError

from jobber.conf import settings


class CustomError(Exception):
    """Wraps the `IndexingError` to be propagated up the stack."""
    # TODO: Find a better name for this.
    pass


@contextmanager
def safe_write(writer, commit=True):
    """Makes sure that the `writer` is properly dealed with if an exception
    is raised inside the context.

    :param: An `IndexWriter` instance.
    :param: Auto-commit flag.

    """
    try:
        yield
    except IndexingError:
        writer.cancel()
        # TODO: raise `CustomError` here.
        raise
    else:
        writer.commit()


class Schema(SchemaClass):
    title = TEXT(stored=True)


class Index(object):
    name = 'jobs'

    def __init__(self, *args, **kwargs):
        directory = settings.SEARCH_INDEX_DIRECTORY
        self.index = index.open_dir(directory, indexname=self.name)

    @classmethod
    def exists(cls):
        """Checks if this index exists."""
        directory = settings.SEARCH_INDEX_DIRECTORY
        return index.exists_in(directory, indexname=cls.name)

    @classmethod
    def create(cls, schema):
        """Creates the index, wiping any existing index.

        :param schema: A `Schema` object.

        """
        directory = settings.SEARCH_INDEX_DIRECTORY
        index.create_in(directory, schema, indexname=cls.name)

    def add_document(self, doc, commit=True, writer=None):
        """Adds a single document to the index.

        You should never pass False for `commit` unless you are also controlling
        the `writer` object. Failure to do so will result in the writer staying
        open so no other thread or process can get a writer or modify the index.

        :param doc: The document to add.
        :param commit: Auto-commit after adding.
        :param writer: An `IndexWriter` instance.

        """
        if writer is None:
            writer = self.index.writer()
        with safe_write(writer, commit):
            writer.add_document(**doc)

    def add_document_bulk(self, docs, commit=True, writer=None):
        """Adds multiple documents to the index.

        The same measures for `commit` should be taken for `add_document_bulk()`
        as for `add_document()`.

        This operation is regarded to be atomic. If any write fails the the
        whole operation will be cancelled. If all writes succeed then a commit
        will take place.

        :param docs: A list of documents to add.
        :param commit: Should we commit after adding all documents?
        :param writer: An `IndexWriter` instance.

        """
        if writer is None:
            writer = self.index.writer()
        with safe_write(writer, commit):
            for doc in docs:
                writer.add_document(**doc)
