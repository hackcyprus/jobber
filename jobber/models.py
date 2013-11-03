"""
jobber.models
~~~~~~~~~~~~~

Model declarations.

"""
from pprint import pformat
from jobber.extensions import db
from jobber.utils import slugify, now


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
    slug = db.Column(db.Unicode(125), nullable=False, unique=True, index=True)

    def __init__(self, **kwargs):
        # We only auto-generate the slug when it's not explicitly passed in the
        # constructor.
        if 'slug' not in kwargs:
            # TODO: have a fallback for failed slugs.
            value = getattr(self, self.SLUG_FIELD)
            self.slug = slugify(value)


class Company(BaseModel):
    __tablename__ = 'companies'

    #: Company id.
    id = db.Column(db.Integer, primary_key=True)

    #: Company name.
    name = db.Column(db.Unicode(75), nullable=False)

    #: Few words describing the company.
    about = db.Column(db.UnicodeText, nullable=True)


class Job(BaseModel, SlugModelMixin):
    __tablename__ = 'jobs'

    JOB_TYPES = {
        1: 'full_time',
        2: 'part_time',
        3: 'contract',
        4: 'internship'
    }

    JOB_TYPES_REVERSED = {v: k for k, v in JOB_TYPES.iteritems()}

    SLUG_FIELD = 'title'

    #: Job id.
    id = db.Column(db.Integer, primary_key=True)

    #: Job title.
    title = db.Column(db.Unicode(100), nullable=False)

    #: Job title slug.
    slug = db.Column(db.Unicode(120), nullable=False)

    #: Job description.
    description = db.Column(db.UnicodeText, nullable=False)

    #: Instructions on how to apply.
    how_to_apply = db.Column(db.UnicodeText, nullable=False)

    #: Job type, one of part-time, full-time, internship, contract.
    job_type = db.Column(db.Integer, nullable=False)

    #: Does the company consider remote workers?
    remote_work = db.Column(db.Boolean, nullable=False, default=False)

    #: Company id as a foreign key relationship.
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    company = db.relationship('Company', backref=db.backref('jobs', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)

    @classmethod
    def machinize_job_type(cls, job_type):
        return cls.JOB_TYPES_REVERSED[job_type]

    @classmethod
    def humanize_job_type(cls, job_type):
        return cls.JOB_TYPES[job_type]

    @property
    def human_job_type(self):
        return self.humanize_job_type(self.job_type)

    @db.validates('job_type')
    def validate_job_type(self, key, job_type):
        if job_type not in self.JOB_TYPES:
            raise ValueError("'{}'' is not a valid job type.".format(job_type))
        return job_type


class Category(BaseModel, SlugModelMixin):
    __tablename__ = 'categories'

    SLUG_FIELD = 'name'

    #: Category id.
    id = db.Column(db.Integer, primary_key=True)

    #: Name of this category.
    name = db.Column(db.Unicode(50), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        SlugModelMixin.__init__(self, **kwargs)
