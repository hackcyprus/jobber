"""
jobber.core.email
~~~~~~~~~~~~~~~~~

Public interface for sending emails using `Flask-Mail`.

"""
from flask import render_template
from flask.ext.mail import Message, Mail, email_dispatched
from jinja2 import TemplateNotFound

from jobber.conf import settings


DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER

mail = Mail()


def render_email_template(template, context):
    """Renders an email template and returns a (subject, text, html) tuple.

    :param template: The template name.
    :param context: The template context as a `dict`.

    """
    def render_or_none(name):
        try:
            return render_template("email/{}/{}.jinja".format(template, name),
                                   **context)
        except TemplateNotFound:
            return None

    return (render_or_none('subject'),
            render_or_none('text'),
            render_or_none('html'))


def send_email_template(template, context, recipients, sender=DEFAULT_SENDER):
    """Sends an email using a template. Uses `send_email` underneath.

    :param template: The template to render.
    :param context: The template context.
    :param recipients: A list of recipient addresses.
    :param sender: The email sender address, optional.

    """
    subject, text, html = render_email_template(template, context)
    return send_email(subject, text, html, recipients, sender=sender)


def send_email(subject, text, html, recipients, sender=DEFAULT_SENDER):
    """Sends an email using a `Flask-Mail` instance.

    :param subject: The email subject.
    :param text: The email body to be sent as text.
    :param html: The email body to be sent as html.
    :param recipients: A list of recipient addresses.
    :param sender: The email sender address, optional.

    """
    msg = Message(subject)
    msg.sender = sender
    msg.recipients = recipients

    if not subject:
        raise Exception('Cannot send email with empty subject!')

    if not text:
        raise Exception('Cannot send email with empty text!')

    msg.body = text

    if html:
        msg.html = html

    mail.send(msg)
    return msg
