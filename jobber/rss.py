"""
jobber.rss
~~~~~~~~~~

Utilities for creating RSS2.0 feeds.

"""
from feedgen.feed import FeedGenerator
from jobber.core.models import Job
from jobber.database import db
from jobber.services import SearchService


# Feed properties.
FEED_LINK = u'http://jobs.hackcyprus.com/feed'
FEED_TITLE = u'Hack Cyprus Jobs Feed'
FEED_SUBTITLE = u'Find a great tech job in Cyprus, Greece or the United Kingdom.'
FEED_LANG = u'en'


DEFAULT_LIMIT = 20


def build_feed_generator():
    gen = FeedGenerator()
    gen.title(FEED_TITLE)
    gen.link(href=FEED_LINK, rel='self', type='application/rss+xml')
    gen.subtitle(FEED_SUBTITLE)
    gen.language(FEED_LANG)
    return gen


def get_all(limit):
    # TODO: These queries should likely be abstracted into a `JobsService`.
    return db.session.query(Job)\
           .filter_by(published=True)\
           .order_by(Job.created)\
           .limit(limit).all()


def search(query, limit):
    service = SearchService()
    return service.search_jobs(query, limit=limit)


def render_feed(query=None, limit=DEFAULT_LIMIT):
    gen = build_feed_generator()

    listings = get_all(limit) if not query else search(query, limit=limit)

    for job in listings:
        url = job.url(external=True)
        company = job.company.name
        location = u"{}, {}".format(job.location.city, job.location.country_name)

        entry = gen.add_entry()
        entry.guid(url)
        entry.link(href=url, rel='alternate')
        entry.title(u"{} at {} in {}".format(job.title, company, location))
        entry.pubdate(job.created.format('YYYY-MM-DD HH:mm:ss ZZ'))
        entry.description(job.description)

    return gen.rss_str(pretty=True)
