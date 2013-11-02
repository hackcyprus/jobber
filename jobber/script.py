"""
jobber.script
~~~~~~~~~~~~~

Script utilities.

"""
import sys
from contextlib import contextmanager
from jobber.factory import create_app


@contextmanager
def context():
    """Sets up a context for the script to run."""
    app = create_app('script')
    with app.app_context() as ctx:
        yield ctx


def die(code):
    """Kills the script with `code` as exit code."""
    sys.exit(code)


def termcolor(code):
    """Decorator that wraps text with `code` for colored terminal output."""
    def wrapper(text):
        return "\033[{}m{}\033[0m".format(code, text)
    return wrapper


red = termcolor('31')
green = termcolor('32')
yellow = termcolor('33')
blue = termcolor('34')
magenta = termcolor('35')
cyan = termcolor('36')
white = termcolor('37')
