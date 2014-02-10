"""
conftest.py
~~~~~~~~~~~

Fixtures for setting up the tests with `pytest` and `Flask`. The convention
here is that fixtures prefixed with '_' are supposed to be internal and used
only by user-facing fixtures.

"""
import os

import pytest
from alembic.command import upgrade
from alembic.config import Config

from env import path_setup
path_setup()

from jobber.conf import settings
from jobber.factory import create_app
from jobber.extensions import db as _db
from jobber.script import blue


TESTDB = 'test_jobber.db'
TESTDB_PATH = "{}/data/{}".format(settings.ROOT, TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


ALEMBIC_CONFIG = "{}/alembic.ini".format(settings.ROOT)


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }
    app = create_app(__name__, settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    # Make sure views and signals are registered.
    import jobber.views

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


def apply_migrations():
    """Applies all alembic migrations."""
    config = Config(ALEMBIC_CONFIG)
    upgrade(config, 'head')


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    print blue('\nInitializing test database.')

    # Make sure we delete any existing test database.
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        print blue('\nDropping all tables from test database.')
        _db.drop_all()
        print blue('Deleting test database.')
        os.unlink(TESTDB_PATH)

    print blue('Applying migrations.')
    apply_migrations()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Starts a new database session within a transaction for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    # Replace the session used by `Flask-SQLAlchemy` with the one we created
    # so it can be used by the models.
    db.session = session

    def teardown():
        # We make sure to rollback and close the session after a test is
        # finished, so that tests do not affect each other.
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def client(app, request):
    return app.test_client()
