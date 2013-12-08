"""
jobber.core.search
~~~~~~~~~~~~~~~~~~

Handles all things search.

"""
from contextlib import contextmanager

from whoosh import index
from whoosh.fields import SchemaClass, TEXT, ID, KEYWORD
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


class SearchableMixin(object):
    """Gives a `to_document()` method to the object, which should return a
    dictionary ready to be indexed in the search index.

    """
    def to_document(self):
        """This method should be overriden in subclasses, since the default
        behaviour is to just return `__dict__`.

        """
        return self.__dict__


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

    def search(self, query, limit=None):
        """Searches the index by parsing `query` and creating a `Query` object.

        :param query: A string containing the users query.
        :param limit: How many results to return, defaults to `None` which will
        return all results.

        """
        parser = MultifieldParser(SEARCHABLE_FIELDS, schema=self.index.schema)
        query = parser.parse(query)
        with self.index.searcher() as searcher:
            hits = searcher.search(query, limit=limit)
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
