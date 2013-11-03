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


def _make_dict(module):
    """Transforms a module into a `dict` containing all the names that the
    module defines.

    """
    if not module:
        return {}
    return {name: getattr(module, name) for name in dir(module)}


_default = _make_dict(default_settings)
_local = _make_dict(local_settings)

class _Settings(object):
    """Placeholder class for settings."""
    def __init__(self, *args):
        for setting in args:
            if setting: self.apply(setting)

    def apply(self, settings):
        for key, value in settings.iteritems():
            if key == key.upper():
                setattr(self, key, value)


# Expose a global `settings` property.
settings = _Settings(_default, _local)
