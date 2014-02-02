"""
jobber.factory
~~~~~~~~~~~~~~

Factory module for creating `Flask` applications.

"""
from __future__ import absolute_import

from logging import StreamHandler, Formatter
from logging.handlers import SysLogHandler

from flask import Flask

from jobber.conf import settings
from jobber.extensions import db
from jobber.core.email import mail


def create_app(package_name, settings_override=None):
    app = Flask(package_name,
                static_folder=settings.STATIC_FOLDER,
                template_folder=settings.TEMPLATES_FOLDER)

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
    """Configures logging to syslog.

    :param app: A `Flask` application.

    """
    level = app.config['LOGGING_LEVEL']

    # Remove existing handlers.
    del app.logger.handlers[:]

    formatter = Formatter('%(name)s %(levelname)s >> %(message)s')

    if app.debug:
        handler = StreamHandler()
    else:
        local0 = SysLogHandler.LOG_LOCAL0
        handler = SysLogHandler(address='/dev/log', facility=local0)

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
