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
from jobber.core.email import mail
from jobber.database import db
from jobber.views import blueprint
from jobber.signals import register_signals


DEFAULT_BLUEPRINTS = [blueprint]


def create_app(package_name, settings_override=None):
    app = Flask(package_name,
                static_folder=settings.STATIC_FOLDER,
                template_folder=settings.TEMPLATES_FOLDER)

    configure_settings(app, override=settings_override)
    configure_database(app)
    configure_signals(app)
    configure_blueprints(app, DEFAULT_BLUEPRINTS)
    configure_logging(app)
    configure_extensions(app)

    return app


def configure_settings(app, override=None):
    """Configures settings and settings overrides.

    :param app: A `Flask` application.
    :param override: Optional settings overrides.

    """
    if override:
        settings.apply(override)
    app.config.from_object(settings)
    return app


def configure_database(app):
    """Configures the database.

    :param app: A `Flask` application.

    """
    db.init_app(app)


def configure_blueprints(app, blueprints):
    """Install all blueprints on the given `app`.

    :param app: A `Flask` application.
    :param override: A list of `Blueprint` instances.

    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_signals(app):
    """Install all signals on the given `app`.

    :param app: A `Flask` application.

    """
    register_signals()


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
    mail.init_app(app)
