"""
jobber.models
~~~~~~~~~~~~~

Model declarations.

"""
from pprint import pformat
from jobber.extensions import db


class BaseModel(db.Model):
    __abstract__ = True

    SKIP_ON_SET = frozenset(['id'])

    def __init__(self, *args, **kwargs):
        self.set_all(**kwargs)

    def __repr__(self):
        name = self.__class__.__name__.capitalize()
        attrs = dict()
        for column in self.__table__.columns:
            attrs[column.name] = getattr(self, column.name)
        return "<{} {}>".format(name, pformat(attrs))

    def set_all(self, **kwargs):
        """Sets all property values of this instance from `kwargs`."""
        for key, value in kwargs.iteritems():
            if key in self.SKIP_ON_SET:
                continue
            if hasattr(self, key):
                setattr(self, key, value)


class Company(BaseModel):
    __tablename__ = 'companies'

    #: Company id.
    id = db.Column(db.Integer, primary_key=True)

    #: Company name.
    name = db.Column(db.String(75), nullable=False)


class Job(BaseModel):
    __tablename__ = 'jobs'

    JOB_TYPES = {
        0: 'full_time',
        1: 'part_time',
        2: 'contract',
        3: 'internship'
    }

    JOB_TYPES_REVERSED = {v: k for k, v in JOB_TYPES.iteritems()}

    #: Job id.
    id = db.Column(db.Integer, primary_key=True)

    #: Job title.
    title = db.Column(db.String(100), nullable=False)

    #: Job description.
    description = db.Column(db.Text, nullable=False)

    #: Instructions on how to apply.
    how_to_apply = db.Column(db.Text, nullable=False)

    #: Job type, one of part-time, full-time, internship, contract.
    job_type = db.Column(db.Integer, nullable=False)

    #: Company id as a foreign key relationship.
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', backref=db.backref('jobs', lazy='dynamic'))

    @classmethod
    def machinize_job_type(cls, job_type):
        return cls.JOB_TYPES_REVERSED[job_type]

    @classmethod
    def humanize_job_Type(cls, job_type):
        return cls.JOB_TYPES[job_type]

    @db.validates('job_type')
    def validate_job_type(self, key, job_type):
        if job_type not in self.JOB_TYPES:
            raise ValueError("'{}'' is not a valid job type.".format(job_type))
        return job_type
