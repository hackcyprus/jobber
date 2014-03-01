from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


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

    @property
    def engine(self):
        if not hasattr(self, '_engine'):
            self._engine = self.create_engine()
        return self._engine

    @property
    def session(self):
        engine = self.engine
        factory = sessionmaker(autocommit=False, autoflush=True, bind=engine)
        return scoped_session(factory)

    def init_app(self, app):
        self.configure_defaults(app)

        # Assumming Flask 0.9 and later
        if hasattr(app, 'teardown_appcontext'):
            teardown = app.teardown_appcontext

        @teardown
        def remove_session(resp_or_exc):
            should_commit = app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']
            if should_commit and resp_or_exc is None:
                self.session.commit()
            self.session.remove()
            return resp_or_exc

        self.app = app

    def configure_defaults(self, app):
        for key, value in self.DEFAULTS:
            app.config.setdefault(key, value)

    def create_engine(self):
        if not hasattr(self, 'app'):
            raise Exception('not initialized')
        dburi = self.app.config['SQLALCHEMY_DATABASE_URI']
        echo = self.app.config['SQLALCHEMY_ECHO']
        options = {
            'convert_unicode': True,
            'echo': echo
        }
        return create_engine(dburi, **options)


db = SQLAlchemy()
