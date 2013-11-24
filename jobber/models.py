"""
jobber.models
~~~~~~~~~~~~~

Model declarations.

"""
from pprint import pformat
from jobber.extensions import db
from jobber.core.search import SearchableMixin
from jobber.core.utils import Mapping, slugify, now


class BaseModel(db.Model):
    """Base model class, adds a `created` timestamp on all deriving models."""

    __abstract__ = True

    #: A timestamp populated on model creation.
    created = db.Column(db.DateTime(timezone=True))

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
            # TODO: have a fallback for failed slugs.
            value = getattr(self, self.SLUG_FIELD)
            self.slug = slugify(value)


class UniqueSlugModelMixin(SlugModelMixin):
    """Forces `slug` to be unique."""
    slug = db.Column(db.Unicode(125), nullable=False, unique=True, index=True)


class Company(BaseModel, UniqueSlugModelMixin):
    __tablename__ = 'companies'

    SLUG_FIELD = 'name'

    #: Company id.
    id = db.Column(db.Integer, primary_key=True)

    #: Company name.
    name = db.Column(db.Unicode(75), nullable=False)

    #: Company website.
    website = db.Column(db.Unicode(100), nullable=True)

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

    #: Contact method, one of url or email.
    contact_method = db.Column(db.Integer, nullable=False)

    #: Contact email, if candidates should apply over email.
    contact_email = db.Column(db.Unicode(150), nullable=True)

    #: Contact url, if candidates should apply over url.
    contact_url = db.Column(db.Unicode(200), nullable=True)

    #: Job type, one of part-time, full-time, internship, contract.
    job_type = db.Column(db.Integer, nullable=False)

    #: Does the company consider remote workers?
    remote_work = db.Column(db.Boolean, nullable=False, default=False)

    #: Company id as a foreign key relationship.
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', backref=db.backref('jobs', lazy='dynamic'))

    #: Location id as a foreign key relationship.
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    location = db.relationship('Location', backref=db.backref('jobs', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)

    @property
    def human_job_type(self):
        return self.JOB_TYPES.map(self.job_type)

    @property
    def human_contact_method(self):
        return self.CONTACT_METHODS.map(self.contact_method)

    @property
    def url(self):
        return u"{}/{}/{}".format(self.id, self.company.slug, self.slug)

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

    @property
    def country_name(self):
        return self.COUNTRIES.map(self.country_code)

    @db.validates('country_code')
    def validate_country_code(self, key, country_code):
        if country_code not in self.COUNTRIES:
            raise ValueError("'{}'' is not a valid country code.".format(country_code))
        return country_code
