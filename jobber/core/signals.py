"""
jobber.core.signals
~~~~~~~~~~~~~~~~~~~

Contains signal registration.

"""
from jobber.core.search import Index
from jobber.models import Job
from jobber.extensions import models_committed
from jobber.app import app


@models_committed.connect_via(app)
def on_models_committed(sender, changes):
    """Received when a list of models is committed to the database.

    :param sender: A `Flask` applications.
    :param changes: A list of `(model, operation)` tuples.

    """
    app.logger.debug('Model commit signal called.')
    print "FUCKFUCKFUCK"
    def update_search_index(job, op):
        """Updates the search index according to the operation.

        :param job: A `Job` instance.
        :param op: The type of operation performed.

        """
        # TODO: index updating should be done in an async task.
        index = Index()
        document = job.to_document()
        if op == 'insert':
            index.add_document(document)
            app.logger.info("Added job with id {} to search index.".format(job.id))
        elif op == 'update':
            pass
        elif op == 'delete':
            pass

    for model, op in changes:
        if not isinstance(model, Job): continue
        update_search_index(model, op)
