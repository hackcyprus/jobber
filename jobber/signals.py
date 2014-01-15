"""
jobber.core.signals
~~~~~~~~~~~~~~~~~~~

Contains signal registration.

"""
from flask import current_app as app

from jobber.core.models import Job
from jobber.extensions import models_committed
from jobber.core.search import Index


# A mapping that specifies what actions need to take place for which models and
# model operations. The actions are specified as strings and looked up in this
# module's `globals()` dict at runtime.
DEFAULT_MODEL_ACTIONMAP = {
    Job: {
        'insert': [
            'update_jobs_index',
        ],
        'update': [
            'update_jobs_index',
        ]
    }
}


def find_model_actions(klass, op, actionmap=None):
    """Finds a list of actions to be performed for the given `klass` and `op`.

    :param klass: A model class.
    :param op: A string describing the operation (insert, update, delete).

    """
    g = globals()
    if actionmap is None:
        actionmap = DEFAULT_MODEL_ACTIONMAP
    actions = actionmap.get(klass, {}).get(op, [])
    return [g.get(a) for a in actions if g.get(a)]


def update_jobs_index(job):
    """Updates the job index according to the published status of the job.

    :param job: A `Job` instance.

    """
    index = Index()
    document = job.to_document()

    if not job.published:
        app.logger.info(u"Job ({}) is unpublished, deleting from index.".format(job.id))
        index.delete_document(document['id'])
        app.logger.info(u"Job ({}) deleted from index.".format(job.id))
    else:
        app.logger.info(u"Job ({}) is published, adding to index.".format(job.id))
        index.add_document(document)
        app.logger.info(u"Job ({}) added to index.".format(job.id))


@models_committed.connect_via(app._get_current_object())
def on_models_committed(sender, changes):
    """Received when a list of models is committed to the database.

    :param sender: A `Flask` applications.
    :param changes: A list of `(model, operation)` tuples.

    """
    app.logger.debug('Model commit signal called.')
    for model, op in changes:
        klass = model.__class__
        actions = find_model_actions(klass, op)

        if not actions:
            app.logger.debug(u'No actions found for ({}, {}).'.format(klass, op))
            continue

        for action in actions:
            action(model)
