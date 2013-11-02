"""
jobber.logging
~~~~~~~~~~~~~~

Custom logging utilities.

"""
from __future__ import absolute_import

import json
from logging import Formatter

try:
    from collections import OrderedDict
    _dict = OrderedDict
except ImportError:
    _dict = dict


FIELDS = ('levelname',
          'lineno',
          'module',
          'funcName',
          'name',
          'message')

VERBOSE_FIELDS = FIELDS + ('thread',
                           'threadName',
                           'pathname',
                           'processName',
                           'filename',
                           'exc_info')


class _JsonFormatter(Formatter):
    required_fields = FIELDS

    def format(self, record):
        record.message = record.getMessage()

        log_record = _dict()

        for field in self.required_fields:
            log_record[field] = record.__dict__.get(field)

        return json.dumps(log_record)


class _VerboseJsonFormatter(_JsonFormatter):
    required_fields = VERBOSE_FIELDS


def make_formatter(verbose=True):
    """Factory method which makes a `Formatter` depending on wanted verbosity.
    A more verbose formatter will output more information about the message, hence
    it is more beneficial in production.

    :param verbose: Verbosity flag.

    """
    return _VerboseJsonFormatter() if verbose else _JsonFormatter()
