"""
jobber.models
~~~~~~~~~~~~~

Model declarations.

This file is pending a move to the `core` package.

"""
import uuid
import hashlib
from pprint import pformat

from jobber.extensions import db
from jobber.core.search import SearchableMixin
from jobber.core.utils import Mapping, slugify, now, ArrowDateTime
from jobber.core.models.helpers import job_tags_relation


class BaseModel(db.Model):
    """Base model class, adds a `created` timestamp on all deriving models."""

    __abstract__ = True

    #: A timestamp populated on model creation.
    created = db.Column(ArrowDateTime(timezone=True))

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
    slug = db.Column(db.Unicode(125), nullable=False, unique=False, index=True)

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
    slug = db.Column(db.Unicode(125), nullable=False, unique=True, index=True)


class PrimaryKeySlugModelMixin(SlugModelMixin):
    """Forces `slug` to be the primary key."""
    slug = db.Column(db.Unicode(125), nullable=False, primary_key=True)


class Company(BaseModel, UniqueSlugModelMixin):
    __tablename__ = 'companies'

    SLUG_FIELD = 'name'

    #: Company id.
    id = db.Column(db.Integer, primary_key=True)

    #: Company name.
    name = db.Column(db.Unicode(75), nullable=False)

    #: Company website.
    website = db.Column(db.Unicode(100), nullable=True)

    #: One-to-many relationship to a `Job`.
    jobs = db.relationship('Job', backref='company')

    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        UniqueSlugModelMixin.__init__(self, **kwargs)


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
    id = db.Column(db.Integer, primary_key=True)

    #: Job title.
    title = db.Column(db.Unicode(100), nullable=False)

    #: Job description.
    description = db.Column(db.UnicodeText, nullable=False)

    #: Is this job published on the site?
    published = db.Column(db.Boolean, nullable=False, default=False)

    #: Contact method, one of url or email.
    contact_method = db.Column(db.Integer, nullable=False)

    #: Contact email, if candidates should apply over email.
    contact_email = db.Column(db.Unicode(150), nullable=True)

    #: Contact url, if candidates should apply over url.
    contact_url = db.Column(db.Unicode(200), nullable=True)

    #: Job type, one of part-time, full-time, internship, contract.
    job_type = db.Column(db.Integer, nullable=False)

    #: Does the company consider remote workers?
    remote_work = db.Column(db.Integer, nullable=False, default=False)

    #: SHA-1 admin token for editing jobs.
    admin_token = db.Column(db.String(40), nullable=False)

    #: Recruiter full name.
    recruiter_name = db.Column(db.Unicode(100), nullable=False)

    #: Recruiter email.
    recruiter_email = db.Column(db.Unicode(100), nullable=False)

    #: Company id as a foreign key relationship.
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    #: Location id as a foreign key relationship.
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

    #: Many-to-many relationship to `Tag`.
    tags = db.relationship('Tag', secondary=job_tags_relation, backref='jobs')

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)

        if not self.admin_token:
            self.admin_token = self.make_admin_token()

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
    def url(self):
        return u"{}/{}/{}".format(self.id, self.company.slug, self.slug)

    @property
    def admin_url(self):
        return u"{}/{}".format(self.id, self.admin_token)

    @db.validates('job_type')
    def validate_job_type(self, key, job_type):
        if job_type not in self.JOB_TYPES:
            raise ValueError("'{}'' is not a valid job type.".format(job_type))
        return job_type

    @db.validates('contact_method')
    def validate_contact_method(self, key, contact_method):
        if contact_method not in self.CONTACT_METHODS:
            raise ValueError("'{}'' is not a valid contact method.".format(contact_method))
        return contact_method

    def make_admin_token(self):
        """Makes an admin token by getting the SHA-1 hash of a `uuid`."""
        rnd = uuid.uuid4().hex
        return hashlib.sha1(rnd).hexdigest()

    def add_tag(self, tag):
        slug = slugify(tag)
        instance = Tag.query.get(slug)

        if instance is None:
            instance = Tag(tag=tag, slug=slug)

        if instance not in self.tags:
            self.tags.append(instance)

        return instance

    def add_tags(self, tags):
        ret = []
        for tag in tags:
            tag = self.add_tag(tag)
            if tag:
                ret.append(tag)
        return ret

    def to_document(self):
        return {
            'id': unicode(self.id),
            'title': self.title,
            'company': self.company.name,
            'location': u"{} {}".format(self.location.city, self.location.country_name),
            'job_type': self.human_job_type
        }


class Category(BaseModel, UniqueSlugModelMixin):
    __tablename__ = 'categories'

    SLUG_FIELD = 'name'

    #: Category id.
    id = db.Column(db.Integer, primary_key=True)

    #: Name of this category.
    name = db.Column(db.Unicode(50), nullable=False)

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
    id = db.Column(db.Integer, primary_key=True)

    #: Location city.
    city = db.Column(db.Unicode(75), nullable=False)

    #: Location country ISO alpha-3 code.
    country_code = db.Column(db.Unicode(3), nullable=False)

    #: One-to-many relationship to a `Job`.
    jobs = db.relationship('Job', backref='location')

    @property
    def country_name(self):
        return self.COUNTRIES.map(self.country_code)

    @db.validates('country_code')
    def validate_country_code(self, key, country_code):
        if country_code not in self.COUNTRIES:
            raise ValueError("'{}'' is not a valid country code.".format(country_code))
        return country_code


class Tag(BaseModel, PrimaryKeySlugModelMixin):
    __tablename__ = 'tags'

    SLUG_FIELD = 'tag'

    #: Tag readable name.
    tag = db.Column(db.Unicode(75), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        PrimaryKeySlugModelMixin.__init__(self, **kwargs)

    def __eq__(self, tag):
        return self.slug == tag.slug
