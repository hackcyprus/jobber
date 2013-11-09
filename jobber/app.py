"""
jobber.app
~~~~~~~~~~

Exposes the `Flask` application.

"""
from jobber import factory

app = factory.create_app(__name__)

print app.session_interface

# Register all views and signals.
import jobber.views
import jobber.core.signals