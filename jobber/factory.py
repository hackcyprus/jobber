"""
jobber.factory
~~~~~~~~~~~~~~

Factory module for creating `Flask` applications.

"""
from __future__ import absolute_import

import logging

from flask import Flask

from jobber.conf import settings
from jobber.extensions import db, mail
from jobber.logging import make_formatter


def create_app(package_name, settings_override=None):
    app = Flask(package_name)

    configure_settings(app, override=settings_override)
    configure_logging(app)
    configure_extensions(app)

    return app


def configure_settings(app, override=None):
    """Configures settings and settings overrides.

    :param app: A `Flask` applications.
    :param override: Optional settings overrides.

    """
    if override:
        settings.apply(override)
    app.config.from_object(settings)
    return app


def configure_logging(app):
    """Configures logging, keeping it intentionally dead simple by logging to
    `stderr` and letting the OS handle it thereafter. Employs a custom formatter
    which logs in JSON for human and machine readability.

    :param app: A `Flask` application.

    """
    level = app.config['LOGGING_LEVEL']

    # Remove existing handlers.
    del app.logger.handlers[:]

    # Attach a `StreamHandler` with a JSON formatter.
    formatter = make_formatter(verbose=not app.debug)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(level)

    app.logger.addHandler(handler)
    app.logger.setLevel(level)

    return app

def configure_extensions(app):
    """Configures all available `Flask` extensions.

    :param app: A `Flask` application.

    """
    db.init_app(app)
    mail.init_app(app)
