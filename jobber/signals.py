"""
jobber.signals
~~~~~~~~~~~~~~

Signal registrations.

"""
from sqlalchemy import event
from blinker import signal

from jobber.core.models import Job
from jobber.core.search import Index
from jobber.database import db


sqlalchemy_flush = signal('sqlalchemy-flush')


# A mapping that specifies what actions need to take place for which models and
# model operations. The actions are specified as strings and looked up in this
# module's `globals()` dict at runtime.
DEFAULT_MODEL_ACTIONMAP = {
    Job: {
        'insert': [
            'index',
        ],
        'update': [
            'update_index',
        ],
        'delete': [
            'deindex'
        ]
    }
}


def index(app, job):
    index = Index()
    document = job.to_document()
    rv = index.add_document(document)
    app.logger.info(u"Job ({}) added to index.".format(job.id))
    return rv


def deindex(app, job):
    index = Index()
    document = job.to_document()
    rv = index.delete_document(document['id'])
    app.logger.info(u"Job ({}) deleted from index.".format(job.id))
    return rv


def update_index(app, job):
    return index(app, job) if job.published else deindex(app, job)


def eligible_actions(klass, operation, actionmap=None):
    g = globals()
    if actionmap is None:
        actionmap = DEFAULT_MODEL_ACTIONMAP
    actions = actionmap.get(klass, {}).get(operation, [])
    return [g.get(a) for a in actions if g.get(a)]


def trigger_actions(instance, operation, app):
    klass = instance.__class__
    name = klass.__name__
    actions = eligible_actions(klass, operation)
    if not actions:
        app.logger.debug(
            u"No actions found for ({}, {})."
            .format(name, operation)
        )
        return

    def prettyprint(actions):
        rv = []
        for action in actions:
            printed = str(action)
            if hasattr(action, '__name__'):
                printed = action.__name__ + '()'
            rv.append(printed)
        return ','.join(rv)

    app.logger.debug(
        "Found eligibe actions for ({}, {}): [{}]."
        .format(name, operation, prettyprint(actions))
    )

    for action in actions:
        action(app, instance)


def on_flush(app, operations):
    for instance, operation in operations:
        trigger_actions(instance, operation, app)


def register_signals(app):
    """Helper for registering all signals during runtime. Since `Flask` uses
    `blinker` for signal support we adapt ORM events and emit `blinker` events.

    """
    # Connect `blinker` signals to handler methods.
    sqlalchemy_flush.connect(on_flush, sender=app)

    # Connect `SQLAlchemy` ORM events to adapter methods.
    def on_flush_adapter(session, context):
        operations = []
        for i in session.new:
            operations.append((i, 'insert'))
        for i in session.dirty:
            operations.append((i, 'update'))
        for i in session.deleted:
            operations.append((i, 'delete'))
        sqlalchemy_flush.send(app, operations=operations)

    event.listen(db.session, 'after_flush', on_flush_adapter)
