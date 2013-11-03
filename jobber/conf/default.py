"""
jobber.conf.default
~~~~~~~~~~~~~~~~~~~

Default configuration.

"""
import logging

DEBUG = True
TESTING = False

SECRET_KEY = 'secret'

SESSION_COOKIE_NAME = 'jobber'
SESSION_COOKIE_SECURE = True

LOGGER_NAME = 'jobber'
LOGGING_LEVEL = logging.DEBUG