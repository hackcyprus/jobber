"""
jobber.core.search
~~~~~~~~~~~~~~~~~~

Handles all things search.

"""
from contextlib import contextmanager

from whoosh import index
from whoosh.fields import SchemaClass, TEXT, ID, KEYWORD, DATETIME
from whoosh.writing import IndexingError
from whoosh.qparser import MultifieldParser
from whoosh.analysis import StemmingAnalyzer

from jobber.conf import settings


# Since we're using a `Multifield` query parser, we need to define which fields
# to search for. These are generally all the fields in the schema apart from
# job id.
SEARCHABLE_FIELDS = ('title', 'description', 'company', 'location', 'job_type', 'tags')


# Global reference to the stemming analyizer we'll use in the schema.
stemming_analyzer = StemmingAnalyzer()


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

    #: The id of the job.
    id = ID(stored=True, unique=True)

    #: The title of the job.
    title = TEXT(analyzer=stemming_analyzer)

    #: The name of the company.
    company = TEXT(analyzer=stemming_analyzer)

    #: Location as a comma-separated string of city and country.
    location = KEYWORD(lowercase=True, scorable=True, commas=True)

    #: The type of job.
    job_type = TEXT(analyzer=stemming_analyzer)

    #: The job tags as a comma-separated string of tag slugs.
    tags = KEYWORD(lowercase=True, scorable=True, commas=True)

    #: When was this job created?
    created = DATETIME(sortable=True)


class SearchableMixin(object):
    """Gives a `to_document()` method to the object, which should return a
    dictionary ready to be indexed in the search index.

    """
    def to_document(self):
        """This method should be overriden in subclasses, since the default
        behaviour is to just return `__dict__`.

        """
        return self.__dict__


class IndexManager(object):
    """Wrapper responsible for creating, deleting and opening `Whoosh` indexes
    on the filesystem.

    """
    @classmethod
    def create(cls, schema, name, directory):
        """Creates the index, wiping any existing index."""
        index.create_in(directory, schema, indexname=name)

    @classmethod
    def open(cls, name, directory):
        """Opens the index."""
        return index.open_dir(directory, indexname=name)

    @classmethod
    def exists(cls, name, directory):
        """Checks if this index exists."""
        return index.exists_in(directory, indexname=name)


class Index(object):
    """Wrapper on top of a `Whoosh` index, provides addition, deletion and
    search capabilities.

    """
    def __init__(self, name=None, directory=None, schema=None):
        if not name:
            name = settings.SEARCH_INDEX_NAME
        if not directory:
            directory = settings.SEARCH_INDEX_DIRECTORY
        if not schema:
            schema = Schema

        self.directory = directory
        self.name = name
        self.schema = Schema

        # The constructor assumes the index already exists.
        self.index = IndexManager.open(self.name, self.directory)

    def search(self, query, limit=None, sort=None):
        """Searches the index by parsing `query` and creating a `Query` object.

        :param query: A string containing the users query.
        :param limit: How many results to return, defaults to `None` which will
        return all results.
        :param sort: The field to sort the results on, given as a tuple of
        (field, direction) i.e ('created', 'asc').

        """
        parser = MultifieldParser(SEARCHABLE_FIELDS, schema=self.index.schema)
        query = parser.parse(query)
        with self.index.searcher() as searcher:
            kwargs = dict(limit=limit)
            if sort:
                field, direction = sort
                kwargs['sortedby'] = field
                kwargs['reverse'] = direction == 'desc'
            hits = searcher.search(query, **kwargs)
            return [hit.fields() for hit in hits]

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

        This operation is regarded to be atomic. If any write fails the whole
        operation will be cancelled. If all writes succeed then a commit will
        take place.

        :param docs: A list of documents to add.
        :param commit: Auto-commit after adding.
        :param writer: An `IndexWriter` instance.

        """
        if writer is None:
            writer = self.index.writer()
        with safe_write(writer, commit):
            for doc in docs:
                writer.add_document(**doc)

    def update_document(self, doc, commit=True, writer=None):
        """Updates a document in the index. The document needs to contain a
        unique property as defined in the schema.

        :param doc: A document to update.
        :param commit: Auto-commit after updating.
        :param writer: An `IndexWriter` instance.

        """
        if writer is None:
            writer = self.index.writer()
        with safe_write(writer, commit):
            writer.update_document(**doc)

    def delete_document(self, docid, commit=True, writer=None):
        """Deletes the document with `docid` in the index.

        :param docid: The id of the document to delete.
        :param commit: Auto-commit after updating.
        :param writer: An `IndexWriter` instance.

        """
        if writer is None:
            writer = self.index.writer()
        with safe_write(writer, commit):
            writer.delete_by_term('id', docid)
