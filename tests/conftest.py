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

from jobber.factory import create_app
from jobber.extensions import db
from jobber.script import blue


TESTDB = 'test_jobber.db'
TESTDB_PATH = "/opt/jobber/data/{}".format(TESTDB)
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH


ALEMBIC_CONFIG = '/opt/jobber/alembic.ini'


def apply_migrations():
    """Applies all alembic migrations."""
    config = Config(ALEMBIC_CONFIG)
    upgrade(config, 'head')


@pytest.fixture(scope='session')
def _db(app, request):
    """Session-wide test database."""
    print blue('\nInitializing test database.')

    # Make sure we delete any existing test database.
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)

    def teardown():
        print blue('\nDropping all tables from test database.')
        db.drop_all()
        print blue('Deleting test database.')
        os.unlink(TESTDB_PATH)

    db.app = app

    print blue('Applying migrations.')
    apply_migrations()

    request.addfinalizer(teardown)
    return db


@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }
    app = create_app(__name__, settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    def teardown():
        ctx.pop()

    return app


@pytest.fixture(scope='function')
def session(app, _db, request):
    """Starts a new database session for a test."""
    session = _db.session
    def teardown():
        # We make sure to rollback and remove the session after the test is
        # finished, so that tests do not affect each other.
        session.rollback()
        session.remove()
    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def client(app, request):
    return app.test_client()
