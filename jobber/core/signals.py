"""
jobber.core.signals
~~~~~~~~~~~~~~~~~~~

Contains signal registration.

"""
from flask import current_app as app

from jobber.core.search import Index
from jobber.models import Job
from jobber.extensions import models_committed
from jobber.core.email import email_dispatched, send_email_template


# A mapping that specifies what actions need to take place for which models and
# model operations. The actions are specified as strings and looked up in this
# module's `globals()` dict at runtime.
DEFAULT_MODEL_ACTIONMAP = {
    Job: {
        'insert': [
            'update_jobs_index',
            'send_instructory_email'
        ],
        'update': [
            'update_jobs_index'
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
        app.logger.info("Job ({}) is unpublished, deleting from index.".format(job.id))
        index.delete_document(document['id'])
        app.logger.info("Job ({}) deleted from index.".format(job.id))
    else:
        app.logger.info("Job ({}) is published, adding to index.".format(job.id))
        index.add_document(document)
        app.logger.info("Job ({}) added to index.".format(job.id))


def send_instructory_email(job):
    """Sends an email to the recruiter with instruction on how to do things.

    :param job: A 'Job' instance.

    """
    recipient = job.recruiter_email
    app.logger.info("About to send instructory email to '%s'.".format(recipient))
    send_email_template('instructory', dict(job=job), [recipient])


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
            app.logger.debug('No actions found for ({}, {}).'.format(klass, op))
            continue

        for action in actions:
            action(model)


@email_dispatched.connect_via(app._get_current_object())
def on_email_dispatched(sender, message):
    """Received when an email is dispatched.

    :param sender: A `Flask` application.
    :param message: A `Message` instance.

    """
    app.logger.debug('Email dispatch signal called.')
    recipients = ','.join(message.recipients)
    msg = "Sent email from %s to [%s] with subject '%s'."
    msg = msg.format(message.sender, recipients, message.subject)
    app.logger.info(msg)
