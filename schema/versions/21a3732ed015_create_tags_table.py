"""create tags table

Revision ID: 21a3732ed015
Revises: 468946541a57
Create Date: 2013-11-30 21:12:41.121135

"""
from alembic import op
import sqlalchemy as sa


revision = '21a3732ed015'
down_revision = '468946541a57'


def upgrade():
    """Creates the `tags` and `job_tags` tables."""
    op.create_table(
        'tags',
        sa.Column('slug', sa.Unicode(125), primary_key=True),
        sa.Column('tag', sa.Unicode(125), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'job_tags',
        sa.Column('job_id', sa.Integer, sa.ForeignKey('jobs.id'), nullable=False),
        sa.Column('tag_slug',
                  sa.Unicode(125),
                  sa.ForeignKey('tags.slug'),
                  nullable=False),
    )


def downgrade():
    """Drops the `tags` and `job_tags` tables."""
    op.drop_table('tags')
    op.drop_table('job_tags')
