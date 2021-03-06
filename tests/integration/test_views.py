# -*- coding: utf-8 -*-
"""
tests.integration.test_views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration tests for the view layer.

"""
from random import choice

import pytest
from flask import url_for
from mock import MagicMock

from jobber.core.models import Location, Company, Job, EmailReviewToken
from jobber.conf import settings
from jobber.core.search import Index


@pytest.fixture(scope='function')
def location():
    return Location(city=u'Lïｍáｓѕ߀ɭ', country_code='CYP')


@pytest.fixture(scope='function')
def company():
    return Company(name=u'remedica')


@pytest.fixture(scope='function')
def job(company, location):
    return Job(title=u'testfoo',
               description=u'testfoo',
               contact_method=1,
               remote_work=False,
               company=company,
               location=location,
               job_type=1,
               recruiter_name=u'jon',
               recruiter_email=u'doe')


@pytest.fixture(scope='function')
def token(job):
    return EmailReviewToken(job=job)


class TestShowJob(object):

    def test_show_okay(self, client, session, job):
        job.published = True
        session.add(job)
        session.commit()

        params = {
            'job_id': job.id,
            'company_slug': job.company.slug,
            'job_slug': job.slug
        }
        url = url_for('views.show', **params)
        response = client.get(url)
        assert response.status_code == 200

    def test_show_unpublished(self, client, session, job):
        session.add(job)
        session.commit()

        params = {
            'job_id': job.id,
            'company_slug': job.company.slug,
            'job_slug': job.slug
        }
        url = url_for('views.show', **params)
        response = client.get(url)
        assert response.status_code == 404

    def test_show_not_matching_company(self, client, session, job):
        session.add(job)
        session.commit()

        params = {
            'job_id': job.id,
            'company_slug': 'bogus',
            'job_slug': job.slug
        }
        url = url_for('views.show', **params)
        response = client.get(url)
        assert response.status_code == 404

    def test_show_not_matching_slug(self, client, session, job):
        session.add(job)
        session.commit()

        params = {
            'job_id': job.id,
            'company_slug': job.company.slug,
            'job_slug': 'bogus'
        }
        url = url_for('views.show', **params)
        response = client.get(url)
        assert response.status_code == 404


class TestEmailReview(object):

    def search(self, query):
        index = Index()
        return index.search(query)

    def test_successful_review(self, monkeypatch, client, session, signals, job, token):
        # Make sure the index is empty before running the test.
        assert len(self.search(job.title)) == 0

        session.add(token)
        session.commit()

        mock = MagicMock()
        monkeypatch.setattr('jobber.views.send_confirmation_email', mock)

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)

        assert response.status_code == 200
        assert session.query(Job).get(job.id).published
        assert session.query(EmailReviewToken).get(token.id).used
        assert len(self.search(job.title)) == 1
        assert mock.called

    def test_unknown_token(self, monkeypatch, client, session, signals, job, token):
        session.add(token)
        session.commit()

        mock = MagicMock()
        monkeypatch.setattr('jobber.views.send_confirmation_email', mock)

        url = "/review/email/{}1241".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 406
        assert not session.query(Job).get(job.id).published
        assert not session.query(EmailReviewToken).get(token.id).used
        assert len(self.search(job.title)) == 0
        assert not mock.called

    def test_already_used_token(self, monkeypatch, client, session, signals, job, token):
        session.add(token)
        token.use()
        session.commit()

        mock = MagicMock()
        monkeypatch.setattr('jobber.views.send_confirmation_email', mock)

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 406
        assert not session.query(Job).get(job.id).published
        assert session.query(EmailReviewToken).get(token.id).used
        assert len(self.search(job.title)) == 0
        assert not mock.called

    def test_unauthorized_email_reviewer(self, monkeypatch, client, session,
                                         signals, job, token):
        session.add(token)
        session.commit()

        mock = MagicMock()
        monkeypatch.setattr('jobber.views.send_confirmation_email', mock)

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': 'jon@doe.com',
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 406
        assert not session.query(Job).get(job.id).published
        assert not session.query(EmailReviewToken).get(token.id).used
        assert len(self.search(job.title)) == 0
        assert not mock.called

    def test_bad_email_content(self, monkeypatch, client, session,
                               signals, job, token):
        session.add(token)
        session.commit()

        mock = MagicMock()
        monkeypatch.setattr('jobber.views.send_confirmation_email', mock)

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'alalala'
        }
        response = client.post(url, data=data)
        assert response.status_code == 406
        assert not session.query(Job).get(job.id).published
        assert not session.query(EmailReviewToken).get(token.id).used
        assert len(self.search(job.title)) == 0
        assert not mock.called

    def test_job_already_published(self, monkeypatch, client, session,
                                   signals, job, token):
        job.published = True
        session.add(token)
        session.commit()

        mock = MagicMock()
        monkeypatch.setattr('jobber.views.send_confirmation_email', mock)

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 200
        assert session.query(Job).get(job.id).published
        assert session.query(EmailReviewToken).get(token.id).used
        assert len(self.search(job.title)) == 1
        assert not mock.called
