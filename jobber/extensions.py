"""
jobber.extensions
~~~~~~~~~~~~~~~~~

Exposes installed `Flask` extensions.

"""
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask.ext.mail import Mail
mail = Mail()