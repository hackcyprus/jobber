"""
jobber.extensions
~~~~~~~~~~~~~~~~~

Exposes installed `Flask` extensions.

"""
from flask.ext.sqlalchemy import (SQLAlchemy,
                                  models_committed,
                                  before_models_committed)

db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()