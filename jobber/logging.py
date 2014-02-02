"""
jobber.logging
~~~~~~~~~~~~~~

Custom logging utilities.

"""
from __future__ import absolute_import

import json
import datetime
from logging import Formatter

try:
    from collections import OrderedDict
    _dict = OrderedDict
except ImportError:
    _dict = dict


FIELDS = ('name',
          'levelname',
          'funcName',
          'message')


class _LogEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M")
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.time):
            return obj.strftime('%H:%M')
        return str(obj)


class JsonFormatter(Formatter):
    required_fields = FIELDS

    def format(self, record):
        record.message = record.getMessage()

        log_record = _dict()

        for field in self.required_fields:
            log_record[field] = record.__dict__.get(field)

        # Add human-readable creation time.
        log_record['asctime'] = self.formatTime(record)

        # Add traceback if any.
        if record.exc_info:
            log_record['traceback'] = self.formatException(record.exc_info)

        return json.dumps(log_record, indent=2, cls=_LogEncoder)
