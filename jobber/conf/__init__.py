"""
jobber.conf
~~~~~~~~~~~

Exposes a `_Settings_` instance with applied overrides from local.py.

"""
from jobber.conf import default as default_settings

try:
    from jobber.conf import local as local_settings
except ImportError:
    local_settings = None


class _Settings(object):
    """Placeholder class for settings."""
    def __init__(self):
        self.apply(default_settings)
        if local_settings:
            self.apply(local_settings)

    def apply(self, settings_module):
        for setting in dir(settings_module):
            if setting == setting.upper():
                value = getattr(settings_module, setting)
                setattr(self, setting, value)


# Expose a global `settings` property.
settings = _Settings()