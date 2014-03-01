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
from jobber.database import db as _db
from jobber.script import blue
from jobber.core.search import Index, Schema
from jobber.signals import register_signals, deregister_signals


DATA_PATH = "{}/data".format(settings.ROOT)

TEST_DATABASE_PATH = "{}/jobber_test.db".format(DATA_PATH)
TEST_DATABASE_URI = 'sqlite:///' + TEST_DATABASE_PATH
TEST_SEARCH_INDEX_NAME = "jobs_test"

ALEMBIC_CONFIG = "{}/alembic.ini".format(settings.ROOT)


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'SEARCH_INDEX_NAME': TEST_SEARCH_INDEX_NAME
    }

    app = create_app(__name__, settings_override)

    # By default, all tests are run without signals for performance. If a
    # test requires signalling support then it has to require the `signals`
    # fixture.
    deregister_signals()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

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
    if os.path.exists(TEST_DATABASE_PATH):
        os.unlink(TEST_DATABASE_PATH)

    def teardown():
        print blue('Deleting test database.')
        os.unlink(TEST_DATABASE_PATH)

    print blue('Applying migrations.')
    apply_migrations()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, monkeypatch, request):
    """Starts a new database session within a transaction for a test."""
    from sqlalchemy.orm import sessionmaker, scoped_session

    connection = db.engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = scoped_session(Session)

    monkeypatch.setattr(db, 'session', session)

    def teardown():
        # We make sure to rollback and close the session after a test is
        # finished, so that tests do not affect each other.
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def signals(session, request):
    register_signals()

    # Since searching can only be done via signals in the app, we create the
    # search index here. It's a quick and easy hack. Note that this will recreate
    # the index everytime so we get a blank index for each test.
    Index.create(Schema)

    def teardown():
        deregister_signals()
    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def client(app, request):
    return app.test_client()
