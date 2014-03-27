# -*- coding: utf-8 -*-
"""
tests.integration.test_index
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration tests for the search index.

"""
import copy
from datetime import timedelta

import pytest

from jobber.core.models import Location, Company, Job
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


class TestSearchIndex(object):

    def test_add_document(self, session, index, job):
        session.add(job)
        session.commit()

        index = Index()
        index.add_document(job.to_document())

        hits = index.search(job.title)
        assert len(hits) == 1
        assert int(hits[0]['id']) == job.id

    def test_update_document(self, session, index, job):
        session.add(job)
        session.commit()

        doc = job.to_document()

        index = Index()
        index.add_document(doc)

        doc['job_type'] = u'updated'
        index.update_document(doc)

        hits = index.search(u'updated')
        assert len(hits) == 1
        assert int(hits[0]['id']) == job.id

    def test_delete_document(self, session, index, job):
        session.add(job)
        session.commit()

        doc = job.to_document()

        index = Index()
        index.add_document(doc)

        hits = index.search(job.title)
        assert len(hits) == 1

        index.delete_document(doc['id'])

        hits = index.search(job.title)
        assert len(hits) == 0

    def test_search_limit(self, session, index, job):
        doc = job.to_document()
        timestamp = doc['created']

        bulk = []
        for i in range(15):
            doc = copy.deepcopy(doc)
            doc['id'] = unicode(i)
            doc['created'] = timestamp - timedelta(days=i)
            bulk.append(doc)

        index = Index()
        index.add_document_bulk(bulk)

        # Search with ascending sort, should return the ids in reverse order.
        hits = index.search(job.title, sort=('created', 'asc'))
        assert [int(hit['id']) for hit in hits] == range(15)[::-1]

        # Search with descending sort.
        hits = index.search(job.title, sort=('created', 'desc'))
        assert [int(hit['id']) for hit in hits] == range(15)
