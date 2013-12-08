"""
jobber.core.models.helpers
~~~~~~~~~~~~~~~~~~~~~~~~~~

Helper utilities and more for the model layer.

"""
from jobber.extensions import db


# Many-to-many association table between jobs and tags.
job_tags_relation = db.Table(
    'job_tags',
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id')),
    db.Column('tag_slug', db.Unicode(125), db.ForeignKey('tags.slug'))
)
