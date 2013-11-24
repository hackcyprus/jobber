"""
jobber.core.signals
~~~~~~~~~~~~~~~~~~~

Contains signal registration.

"""
from jobber.core.search import Index
from jobber.models import Job
from jobber.extensions import models_committed
from jobber.app import app


def update_jobs_search_index(job, op):
    """Updates the `Job` search index according to the operation.

    :param job: A `Job` instance.
    :param op: The type of operation performed.

    """
    # TODO: index updating should be done in an async task.
    if not job.published:
        app.logger.info("Job ({}) is unpublished and not added to index."
                        .format(job.id))
        return

    index = Index()
    document = job.to_document()
    if op == 'insert':
        index.add_document(document)
        app.logger.info("Job ({}) add to index.".format(job.id))
    elif op == 'update':
        pass
    elif op == 'delete':
        pass


@models_committed.connect_via(app)
def on_models_committed(sender, changes):
    """Received when a list of models is committed to the database.

    :param sender: A `Flask` applications.
    :param changes: A list of `(model, operation)` tuples.

    """
    app.logger.debug('Model commit signal called.')
    for model, op in changes:
        if not isinstance(model, Job): continue
        update_jobs_search_index(model, op)
