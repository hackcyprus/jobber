"""
conftest.py
~~~~~~~~~~~

Fixtures for setting up the tests with `pytest` and `Flask`. The convention
here is that fixtures prefixed with '_' are supposed to be internal and used
only by user-facing fixtures.

"""
import pytest

from env import path_setup
path_setup()

from jobber.factory import create_app
from jobber.extensions import db


TEST_DATABASE_URI = 'sqlite:////opt/jobber/schema/test_jobber.db'


@pytest.fixture(scope='session')
def _db(app, request):
    """Session-wide test database."""
    def teardown():
        db.drop_all()

    # The way we initialize the app in `factory.create_app()` does not allow
    # for running `db.create_all()` without a request context so we manually
    # assign `db.app` to the test application.
    db.app = app
    db.create_all()

    request.addfinalizer(teardown)
    return db


@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }
    return create_app(__name__, settings_override)


@pytest.fixture(scope='function')
def session(app, _db, request):
    """Starts a new database session for a test."""
    session = _db.session
    def teardown():
        # We make sure to rollback the session after the test is finished, so
        # that tests do not affect each other.
        session.rollback()
    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def client(app, request):
    return app.test_client()
