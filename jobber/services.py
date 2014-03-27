from jobber.core.search import Index
from jobber.core.models import Job
from jobber.database import db


class SearchService(object):

    def search_jobs(self, query, sort=None, limit=None):
        index = Index()
        hits = []

        kwargs = dict()
        if sort:
            kwargs['sort'] = sort
        if limit:
            kwargs['limit'] = limit

        for hit in index.search(query, **kwargs):
            job = db.session.query(Job).get(hit['id'])
            # Make sure that we don't accidentally return an unpublished job
            # that happened to be in the search index.
            if job and job.published:
                hits.append(job)

        return hits
