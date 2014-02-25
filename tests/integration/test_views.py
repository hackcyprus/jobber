# -*- coding: utf-8 -*-
"""
tests.integration.test_views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration tests for the view layer.

"""
from random import choice
import pytest
from jobber.core.models import Location, Company, Job, EmailReviewToken
from jobber.conf import settings


@pytest.fixture(scope='function')
def location():
    return Location(city=u'Lïｍáｓѕ߀ɭ', country_code='CYP')


@pytest.fixture(scope='function')
def company():
    return Company(name=u'remedica')


@pytest.fixture(scope='function')
def job(company, location):
    return Job(id=1,
               title='testfoo',
               description='testfoo',
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


class TestEmailReview(object):

    def test_successful_review(self, client, session, job, token):
        session.add(job)
        session.add(token)
        session.commit()

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)

        assert response.status_code == 200
        assert Job.query.get(job.id).published
        assert EmailReviewToken.query.get(token.id).used

    def test_unknown_token(self, client, session, job, token):
        session.add(job)
        session.add(token)
        session.commit()

        url = "/review/email/{}1241".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 404
        assert not Job.query.get(job.id).published
        assert not EmailReviewToken.query.get(token.id).used

    def test_already_used_token(self, client, session, job, token):
        session.add(job)
        session.add(token)

        token.use()

        session.commit()

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 404
        assert not Job.query.get(job.id).published
        assert EmailReviewToken.query.get(token.id).used

    def test_unauthorized_email_reviewer(self, client, session, job, token):
        session.add(job)
        session.add(token)
        session.commit()

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': 'jon@doe.com',
            'stripped-text': 'ok'
        }
        response = client.post(url, data=data)
        assert response.status_code == 404
        assert not Job.query.get(job.id).published
        assert not EmailReviewToken.query.get(token.id).used

    def test_bad_email_content(self, client, session, job, token):
        session.add(job)
        session.add(token)
        session.commit()

        url = "/review/email/{}".format(token.token)
        data = {
            'sender': choice(settings.EMAIL_REVIEWERS),
            'stripped-text': 'alalala'
        }
        response = client.post(url, data=data)
        assert response.status_code == 404
        assert not Job.query.get(job.id).published
        assert not EmailReviewToken.query.get(token.id).used
