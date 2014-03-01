"""
jobber.signals
~~~~~~~~~~~~~~

Signal registrations.

"""
import logging

from sqlalchemy import event
from blinker import signal

from jobber.core.models import Job
from jobber.core.search import Index
from jobber.database import db


logger = logging.getLogger('jobber')


sqlalchemy_flush = signal('sqlalchemy-flush')


# A mapping that specifies what actions need to take place for which models and
# model operations. The actions are specified as strings and looked up in this
# module's `globals()` dict at runtime.
DEFAULT_MODEL_ACTIONMAP = {
    Job: {
        'insert': [
            'update_index',
        ],
        'update': [
            'update_index',
        ],
        'delete': [
            'deindex'
        ]
    }
}


def index(job):
    index = Index()
    document = job.to_document()
    rv = index.add_document(document)
    logger.info(u"Job ({}) added to index.".format(job.id))
    return rv


def deindex(job):
    index = Index()
    document = job.to_document()
    rv = index.delete_document(document['id'])
    logger.info(u"Job ({}) deleted from index.".format(job.id))
    return rv


def update_index(job):
    return index(job) if job.published else deindex(job)


def eligible_actions(klass, operation, actionmap=None):
    g = globals()
    if actionmap is None:
        actionmap = DEFAULT_MODEL_ACTIONMAP
    actions = actionmap.get(klass, {}).get(operation, [])
    return [g.get(a) for a in actions if g.get(a)]


def trigger_actions(instance, operation):
    klass = instance.__class__
    name = klass.__name__
    actions = eligible_actions(klass, operation)
    if not actions:
        logger.debug(
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

    logger.debug(
        "Found eligibe actions for ({}, {}): [{}]."
        .format(name, operation, prettyprint(actions))
    )

    for action in actions:
        action(instance)


def on_flush(sender, operations):
    for instance, operation in operations:
        trigger_actions(instance, operation)


def on_flush_adapter(session, context):
    operations = []
    for i in session.new:
        operations.append((i, 'insert'))
    for i in session.dirty:
        operations.append((i, 'update'))
    for i in session.deleted:
        operations.append((i, 'delete'))
    sqlalchemy_flush.send(session, operations=operations)


def register_signals():
    """Helper for registering all signals during runtime. Since `Flask` uses
    `blinker` for signal support we adapt ORM events and emit `blinker` events.

    """
    # Connect `blinker` signals to handler methods.
    sqlalchemy_flush.connect(on_flush)

    # Connect `SQLAlchemy` ORM events to adapter methods.
    event.listen(db.session, 'after_flush', on_flush_adapter)


def deregister_signals():
    """Helper for deregistering all signals at runtime. Helpful during tests."""
    event.remove(db.session, 'after_flush', on_flush_adapter)
    sqlalchemy_flush.disconnect(on_flush)
