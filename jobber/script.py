"""
jobber.script
~~~~~~~~~~~~~

Script utilities.

"""
import sys
from jobber.factory import create_app
from jobber.extensions import db


def run(main, *args):
    """Runs the script in an application context and manages the session cycle.

    :param main: A function to run.
    :param *args: Positional arguments to the `main` function.

    """
    app = create_app(__name__)
    with app.app_context():
        # Register all signals before running the script. Hackish.
        import jobber.core.signals

        # Run the script and commit/rollback accordingly.
        session = db.session
        try:
            args += (session,)
            main(*args)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


def die(reason):
    """Prints `reason` and kills script with exit code 1.

    :param reason: Reason phrase.

    """
    print red(reason)
    sys.exit(1)


def prompt(message, yesno=False):
    """Prompts the user for a value.

    :param message: A string to display at the prompt.
    :param yesno: A flag indicating whether the user should reply y/n.

    """
    if yesno:
        message = "{} [y/N]".format(message)
    value = raw_input("{}: ".format(message))
    return value.lower() == 'y' if yesno else value


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
