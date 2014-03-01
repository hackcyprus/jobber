import functools
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def threadsafe(fn):
    """Makes the execution of `fn` thread-safe."""
    lock = Lock()
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        lock.acquire()
        try:
            return fn(self, *args, **kwargs)
        finally:
            lock.release()
    return wrapper


def memoize(fn):
    """Remembers the return value of `fn` for the given `args` and `kwargs`. If
    `fn` is called again with the same combination of `args` and `kwargs` no
    computation takes place.

    """
    memo = {}
    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        key = fn.__name__ + str(args) + str(kwargs)
        if key not in memo:
            memo[key] = fn(self, *args, **kwargs)
        return memo[key]
    return wrapper


class NotInitialized(Exception):
    pass


class SQLAlchemy(object):

    DEFAULTS = (
        ('SQLALCHEMY_DATABASE_URI', 'sqlite://'),
        ('SQLALCHEMY_ECHO', False),
        ('SQLALCHEMY_POOL_SIZE', None),
        ('SQLALCHEMY_POOL_TIMEOUT', None),
        ('SQLALCHEMY_POOL_RECYCLE', None),
        ('SQLALCHEMY_MAX_OVERFLOW', None),
        ('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
    )

    def __init__(self):
        self.engine = None
        self.session = None

    def _ensure_initialized(self):
        if not hasattr(self, 'app'):
            raise NotInitialized(
                'The `SQLAlchemy` wrapper is not initialized. Make sure you '
                'call init_app() before any operations take place.'
            )

    @memoize
    def _create_session(self):
        self._ensure_initialized()

        engine = self.engine
        if not engine:
            engine = self._create_engine()

        factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Returning a `scoped_session` takes care of threading issues as each
        # thread will get a local session.
        return scoped_session(factory)

    @memoize
    @threadsafe
    def _create_engine(self):
        self._ensure_initialized()

        dburi = self.app.config['SQLALCHEMY_DATABASE_URI']
        echo = self.app.config['SQLALCHEMY_ECHO']
        options = {
            'convert_unicode': True,
            'echo': echo
        }

        return create_engine(dburi, **options)

    def init_app(self, app):
        self.configure_defaults(app)

        # Assumming Flask 0.9 and later
        @app.teardown_appcontext
        def remove_session(resp_or_exc):
            should_commit = app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']
            if should_commit and resp_or_exc is None:
                self.session.commit()
            self.session.remove()
            return resp_or_exc

        self.app = app
        self.engine = self._create_engine()
        self.session = self._create_session()

    def configure_defaults(self, app):
        for key, value in self.DEFAULTS:
            app.config.setdefault(key, value)


db = SQLAlchemy()
