# -*- coding: utf-8 -*-
"""
tests.unit.test_email
~~~~~~~~~~~~~~~~~~~~~

Tests email sending and template rendering.

"""
import os
import uuid
import shutil

import pytest
from mock import MagicMock

from jobber.core.email import (DEFAULT_SENDER,
                               mail,
                               render_email_template,
                               send_email_template,
                               send_email)


ROOT = '/opt/jobber/'


@pytest.fixture
def template(request):
    """Creates a test email template."""
    def wrapper(parts):
        # Make a random directory.
        name = uuid.uuid4().hex[:7]
        tmpdir = os.path.join(ROOT, 'jobber', 'templates', 'email', name)
        os.mkdir(tmpdir)

        # Create the necessary templates.
        for part in parts:
            tmpl_name = "{}.jinja".format(part)
            with open(os.path.join(tmpdir, tmpl_name), 'w') as f:
                f.write('test {{var}}')

        def teardown():
            shutil.rmtree(tmpdir)

        # Make sure we cleanup the directory.
        request.addfinalizer(teardown)

        return name

    return wrapper


@pytest.mark.parametrize('input,expected', [

    # All three parts exist.
    (('subject', 'text', 'html'), ('test foo', 'test foo', 'test foo')),

    # Email has no html body.
    (('subject', 'text'), ('test foo', 'test foo', None)),

    # Email has no subject.
    (('text', 'html'), (None, 'test foo', 'test foo')),

    # Email has no text body.
    (('subject', 'html'), ('test foo', None, 'test foo'))

])
def test_render_email_template(app, template, input, expected):
    context = {'var': 'foo'}
    name = template(input)
    subject, text, html = render_email_template(name, context)
    assert subject == expected[0]
    assert text == expected[1]
    assert html == expected[2]


def test_send_email_template(app, template, monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('jobber.core.email.send_email', mock)

    name = template(['subject', 'text'])
    recipients = ['test@foo.org']

    send_email_template(name, {'var': 'foo'}, recipients)
    mock.assert_called_with('test foo', 'test foo', None,
                            recipients, sender=DEFAULT_SENDER)


def test_send_email(app):
    recipients = ['test@foo.org']
    with mail.record_messages() as outbox:
        send_email('foo', 'bar', '<div>bar</div>', recipients)
        assert len(outbox) == 1
        assert outbox[0].subject == 'foo'
        assert outbox[0].body == 'bar'
        assert outbox[0].html == '<div>bar</div>'


def test_send_invalid_email(app):
    recipients = ['test@foo.org']
    with pytest.raises(Exception):
        send_email(None, 'bar', '<div>bar</div>', recipients)
        send_email('', 'bar', '<div>bar</div>', recipients)
        send_email('foo', None, '<div>bar</div>', recipients)
        send_email('foo', '', '<div>bar</div>', recipients)
