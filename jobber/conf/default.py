"""
jobber.conf.default
~~~~~~~~~~~~~~~~~~~

Default configuration.

"""
import logging

DEBUG = True
TESTING = False

PORT = 8000

SECRET_KEY = 'secret'

SESSION_COOKIE_NAME = 'jobber'
SESSION_COOKIE_SECURE = True

LOGGER_NAME = 'jobber'
LOGGING_LEVEL = logging.DEBUG

SQLALCHEMY_DATABASE_URI = '<uri>'
SQLALCHEMY_ECHO = True

SEARCH_INDEX_DIRECTORY = '<dir>'
SEARCH_INDEX_NAME = '<name>'