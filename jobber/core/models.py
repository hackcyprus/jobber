"""
jobber.core.models
~~~~~~~~~~~~~~~~~~

Core model declarations.

"""
import uuid
import hashlib
from pprint import pformat

import sqlalchemy as sa
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from flask import url_for

from jobber.core.search import SearchableMixin
from jobber.core.utils import Mapping, slugify, now
from jobber.core.utils import ensure_protocol, ArrowDateTime, strip_html
from jobber.database import db


Base = declarative_base()


class BaseModel(Base):
    """Base model class, adds a `created` timestamp on all deriving models."""

    __abstract__ = True

    #: A timestamp populated on model creation.
    created = sa.Column(ArrowDateTime(timezone=True))

    def __init__(self, *args, **kwargs):
        if self.created is None:
            self.created = now()
        super(BaseModel, self).__init__(*args, **kwargs)

    def __repr__(self):
        name = self.__class__.__name__.capitalize()
        attrs = dict()
        for column in self.__table__.columns:
            attrs[column.name] = getattr(self, column.name)
        return "<{} {}>".format(name, pformat(attrs))


class SlugModelMixin(object):
    """Adds a `slug` column to the model from the `SLUG_FIELD` value."""

    SLUG_FIELD = None

    #: Slugified version of `SLUG_FIELD`.
    slug = sa.Column(sa.Unicode(125), nullable=False, unique=False, index=True)

    def __init__(self, **kwargs):
        # We only auto-generate the slug when it's not explicitly passed in the
        # constructor.
        if 'slug' not in kwargs:
            self.populate_slug()

    def populate_slug(self):
        """Populates the slug in this model. If the `SLUG_FIELD` value is `None`,
        then this method is a noop.

        """
        # TODO: have a fallback for failed slugs.
        value = getattr(self, self.SLUG_FIELD)
        if value is None: return
        self.slug = slugify(value)


class UniqueSlugModelMixin(SlugModelMixin):
    """Forces `slug` to be unique."""
    slug = sa.Column(sa.Unicode(125), nullable=False, unique=True, index=True)


class PrimaryKeySlugModelMixin(SlugModelMixin):
    """Forces `slug` to be the primary key."""
    slug = sa.Column(sa.Unicode(125), nullable=False, primary_key=True)


class Company(BaseModel, SlugModelMixin):
    __tablename__ = 'companies'

    SLUG_FIELD = 'name'

    #: Company id.
    id = sa.Column(sa.Integer, primary_key=True)

    #: Company name.
    name = sa.Column(sa.Unicode(75), nullable=False)

    #: Company website.
    website = sa.Column(sa.Unicode(200), nullable=True)

    #: One-to-many relationship to a `Job`.
    jobs = relationship('Job', backref='company')

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)

    @property
    def website_with_protocol(self):
        return ensure_protocol(self.website)


# Many-to-many association table between jobs and tags.
job_tags_association = sa.Table('job_tags', Base.metadata,
    sa.Column('job_id', sa.Integer, sa.ForeignKey('jobs.id')),
    sa.Column('tag_slug', sa.Unicode(125), sa.ForeignKey('tags.slug'))
)


class Job(BaseModel, SlugModelMixin, SearchableMixin):
    __tablename__ = 'jobs'

    CONTACT_METHODS = Mapping({
        1: u'Link',
        2: u'Email'
    })

    JOB_TYPES = Mapping({
        1: u'Full Time',
        2: u'Part Time',
        3: u'Contract',
        4: u'Internship'
    })

    REMOTE_WORK_OPTIONS = Mapping({
        1: u'Yes',
        2: u'No',
        3: u'Negotiable'
    })

    SLUG_FIELD = 'title'

    #: Job id.
    id = sa.Column(sa.Integer, primary_key=True)

    #: Job title.
    title = sa.Column(sa.Unicode(100), nullable=False)

    #: Job description.
    description = sa.Column(sa.UnicodeText, nullable=False)

    #: Is this job published on the site?
    published = sa.Column(sa.Boolean, nullable=False, default=False)

    #: Contact method, one of url or email.
    contact_method = sa.Column(sa.Integer, nullable=False)

    #: Contact email, if candidates should apply over email.
    contact_email = sa.Column(sa.Unicode(150), nullable=True)

    #: Contact url, if candidates should apply over url.
    contact_url = sa.Column(sa.Unicode(200), nullable=True)

    #: Job type, one of part-time, full-time, internship, contract.
    job_type = sa.Column(sa.Integer, nullable=False)

    #: Does the company consider remote workers?
    remote_work = sa.Column(sa.Integer, nullable=False, default=False)

    #: SHA-1 admin token for editing jobs.
    admin_token = sa.Column(sa.String(40), nullable=False)

    #: Recruiter full name.
    recruiter_name = sa.Column(sa.Unicode(100), nullable=False)

    #: Recruiter email.
    recruiter_email = sa.Column(sa.Unicode(150), nullable=False)

    #: Company id as a foreign key relationship.
    company_id = sa.Column(sa.Integer, sa.ForeignKey('companies.id'))

    #: Location id as a foreign key relationship.
    location_id = sa.Column(sa.Integer, sa.ForeignKey('locations.id'))

    #: Many-to-many relationship to `Tag`.
    tags = relationship('Tag', secondary=job_tags_association, backref='jobs')

    #: One-to-many relationship to `EmailReviewToken`.
    jobs = relationship('EmailReviewToken', backref='job')

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)

        if not self.admin_token:
            self.admin_token = self.make_admin_token()

    @property
    def description_text(self):
        """Returns the description without HTML entities."""
        return strip_html(self.description)

    @property
    def human_job_type(self):
        return self.JOB_TYPES.map(self.job_type)

    @property
    def human_contact_method(self):
        return self.CONTACT_METHODS.map(self.contact_method)

    @property
    def human_remote_work(self):
        return self.REMOTE_WORK_OPTIONS.map(self.remote_work)

    @property
    def contact_url_with_protocol(self):
        return ensure_protocol(self.contact_url)

    def _url(self, external=True):
        kwargs = {
            'job_id': self.id,
            'company_slug': self.company.slug,
            'job_slug': self.slug,
            '_external': external
        }
        return url_for('views.show', **kwargs)

    @property
    def tag_slugs(self):
        return [tag.slug for tag in self.tags]

    def url(self, external=False):
        if not self.id:
            return None
        kwargs = {
            'job_id': self.id,
            'company_slug': self.company.slug,
            'job_slug': self.slug,
            '_external': external
        }
        return url_for('views.show', **kwargs)

    def edit_url(self, external=False):
        if not self.id:
            return None
        kwargs = {
            'job_id': self.id,
            'token': self.admin_token,
            '_external': external
        }
        return url_for('views.edit', **kwargs)

    @validates('job_type')
    def validate_job_type(self, key, job_type):
        if job_type not in self.JOB_TYPES:
            raise ValueError("'{}'' is not a valid job type.".format(job_type))
        return job_type

    @validates('contact_method')
    def validate_contact_method(self, key, contact_method):
        if contact_method not in self.CONTACT_METHODS:
            raise ValueError("'{}'' is not a valid contact method.".format(contact_method))
        return contact_method

    def make_admin_token(self):
        """Makes an admin token by getting the SHA-1 hash of a `uuid`."""
        rnd = uuid.uuid4().hex
        return hashlib.sha1(rnd).hexdigest()

    def add_tag(self, tag):
        """Adds a new tag to this job.

        :param tag: A string.

        """
        instance = Tag.get_or_create(tag)
        if instance not in self.tags:
            self.tags.append(instance)
        return instance

    def add_tags(self, tags):
        """Adds multiple tags by utilizing `add_tag()`.

        :param tags: A list of strings.

        """
        ret = []
        for tag in tags:
            tag = self.add_tag(tag)
            if tag:
                ret.append(tag)
        return ret

    def replace_tags(self, tags):
        """Replaces current tags with `tags`.

        :param tags: A list of strings.

        """
        while self.tags:
            tag = self.tags[0]
            self.tags.remove(tag)
        self.add_tags(tags)

    def to_document(self):
        return {
            'id': unicode(self.id),
            'title': self.title,
            'company': self.company.name,
            'location': u"{},{}".format(self.location.city, self.location.country_name),
            'job_type': self.human_job_type,
            'tags': u','.join(self.tag_slugs),
            'created': self.created.datetime
        }


class Category(BaseModel, UniqueSlugModelMixin):
    __tablename__ = 'categories'

    SLUG_FIELD = 'name'

    #: Category id.
    id = sa.Column(sa.Integer, primary_key=True)

    #: Name of this category.
    name = sa.Column(sa.Unicode(50), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)


class Location(BaseModel):
    __tablename__ = 'locations'

    # Initial supported countries until we open up more.
    COUNTRIES = Mapping({
        u'CYP': u'Cyprus',
        u'GRC': u'Greece',
        u'GBR': u'United Kingdom'
    })

    #: Location id.
    id = sa.Column(sa.Integer, primary_key=True)

    #: Location city.
    city = sa.Column(sa.Unicode(75), nullable=False)

    #: Location country ISO alpha-3 code.
    country_code = sa.Column(sa.Unicode(3), nullable=False)

    #: One-to-many relationship to a `Job`.
    jobs = relationship('Job', backref='location')

    @property
    def country_name(self):
        return self.COUNTRIES.map(self.country_code)

    @validates('country_code')
    def validate_country_code(self, key, country_code):
        if country_code not in self.COUNTRIES:
            raise ValueError("'{}'' is not a valid country code.".format(country_code))
        return country_code


class Tag(BaseModel, PrimaryKeySlugModelMixin):
    __tablename__ = 'tags'

    SLUG_FIELD = 'tag'

    #: Tag readable name.
    tag = sa.Column(sa.Unicode(75), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        PrimaryKeySlugModelMixin.__init__(self, **kwargs)

    def __eq__(self, tag):
        return self.slug == tag.slug

    @classmethod
    def get_or_create(cls, tag):
        slug = slugify(tag)
        instance = db.session.query(Tag).get(slug)
        if instance is None:
            instance = Tag(tag=tag, slug=slug)
        return instance


class EmailReviewToken(BaseModel):
    __tablename__ = 'email_review_tokens'

    #: Token id.
    id = sa.Column(sa.Integer, primary_key=True)

    #: Token value.
    token = sa.Column(sa.Unicode(10), nullable=False, unique=False, index=True)

    #: Flag showing whether the token was used.
    used = sa.Column(sa.Boolean, nullable=False, default=False)

    #: A timestamp for when this token was used.
    used_at = sa.Column(ArrowDateTime(timezone=True))

    #: Job id as a foreign key relationship.
    job_id = sa.Column(sa.Integer, sa.ForeignKey('jobs.id'))

    def __init__(self, *args, **kwargs):
        if self.token is None:
            self.token = uuid.uuid4().hex[:10]
        super(EmailReviewToken, self).__init__(*args, **kwargs)

    def use(self):
        self.used = True
        self.used_at = now()
