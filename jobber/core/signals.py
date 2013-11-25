"""
jobber.core.signals
~~~~~~~~~~~~~~~~~~~

Contains signal registration.

"""
from jobber.core.search import Index
from jobber.models import Job, AdminToken
from jobber.extensions import models_committed
from jobber.app import app
from jobber.extensions import db


# A mapping that specifies what actions need to take place for which models and
# model operations. The actions are specified as strings and looked up in this
# module's `globals()` dict at runtime.
DEFAULT_ACTIONMAP = {
    Job: {
        'insert': [
            'index_job',
            'create_admin_token'
        ]
    }
}


def find_actions(klass, op, actionmap=None):
    """Finds a list of actions to be performed for the given `klass` and `op`.

    :param klass: A model class.
    :param op: A string describing the operation (insert, update, delete).

    """
    g = globals()
    if actionmap is None:
        actionmap = DEFAULT_ACTIONMAP
    actions = actionmap.get(klass, {}).get(op, [])
    return [g.get(a) for a in actions if g.get(a)]


def index_job(job):
    """Adds `job` to the search index.

    :param job: A `Job` instance.

    """
    if not job.published:
        msg = "Job ({}) is unpublished and will not be indexed.".format(job.id)
        app.logger.info(msg)
        return

    index = Index()
    document = job.to_document()
    index.add_document(document)
    app.logger.info("Job ({}) add to index.".format(job.id))


def create_admin_token(job):
    """Creates an admin token for the given `job`.

    :param job: A `Job` instance.

    """
    admin_token = AdminToken(job_id=job.id)
    db.session.add(admin_token)
    db.session.commit(admin_token)


@models_committed.connect_via(app)
def on_models_committed(sender, changes):
    """Received when a list of models is committed to the database.

    :param sender: A `Flask` applications.
    :param changes: A list of `(model, operation)` tuples.

    """
    app.logger.debug('Model commit signal called.')
    for model, op in changes:
        klass = model.__class__
        actions = find_actions(klass, op)

        if not actions:
            app.logger.debug('No actions found for ({}, {}).'.format(klass, op))
            continue

        for action in actions:
            action(model)
