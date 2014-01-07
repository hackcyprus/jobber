"""
jobber.conf.default
~~~~~~~~~~~~~~~~~~~

Default configuration.

"""
import logging

DEBUG = True
TESTING = False

PORT = 8000

SECRET_KEY = '<secret>'

APPLICATION_ROOT = None

SERVER_NAME = '<server_name>'

ROOT = '<root>'

STATIC_FOLDER = '<static>'
TEMPLATES_FOLDER = '<templates>'

SESSION_COOKIE_NAME = 'jobber'

LOGGER_NAME = 'jobber'
LOGGING_LEVEL = logging.DEBUG

SQLALCHEMY_DATABASE_URI = '<uri>'
SQLALCHEMY_ECHO = True

SEARCH_INDEX_DIRECTORY = '<dir>'
SEARCH_INDEX_NAME = '<name>'

MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_DEFAULT_SENDER = '<sender>'
MAIL_ADMIN_RECIPIENT = '<admin>'
