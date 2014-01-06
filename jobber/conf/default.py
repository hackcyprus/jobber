"""
jobber.conf.default
~~~~~~~~~~~~~~~~~~~

Default configuration.

"""
import os
import logging

DEBUG = True
TESTING = False

PORT = 8000

SECRET_KEY = 'secret'

APPLICATION_ROOT = None

ROOT = '/opt/jobber'

STATIC_FOLDER = os.path.join(ROOT, 'jobber', 'static')
TEMPLATES_FOLDER = os.path.join(ROOT, 'jobber', 'templates')

SESSION_COOKIE_NAME = 'jobber'

LOGGER_NAME = 'jobber'
LOGGING_LEVEL = logging.DEBUG

SQLALCHEMY_DATABASE_URI = '<uri>'
SQLALCHEMY_ECHO = True

SEARCH_INDEX_DIRECTORY = '<dir>'
SEARCH_INDEX_NAME = '<name>'

MAIL_SERVER = 'localhost'
MAIL_PORT = 25