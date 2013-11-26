"""create jobs table

Revision ID: 34a1034caa3b
Revises: 34b87469a386
Create Date: 2013-11-02 00:30:42.855428

"""
from alembic import op
import sqlalchemy as sa


revision = '34a1034caa3b'
down_revision = '34b87469a386'


def upgrade():
    """Creates the `jobs` table."""
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime(timezone=True)),
        sa.Column('title', sa.Unicode(100), nullable=False),
        sa.Column('slug', sa.Unicode(125), nullable=False, unique=False, index=True),
        sa.Column('published', sa.Boolean, nullable=False, default=False),
        sa.Column('description', sa.UnicodeText, nullable=True),
        sa.Column('contact_method', sa.Integer, nullable=False),
        sa.Column('contact_email', sa.Unicode(150), nullable=True),
        sa.Column('contact_url', sa.Unicode(200), nullable=True),
        sa.Column('job_type', sa.Integer, nullable=False),
        sa.Column('remote_work', sa.Integer, nullable=False, default=False),
        sa.Column('admin_token', sa.String(40), nullable=False, unique=True, index=True),
        sa.Column('company_id',
                  sa.Integer,
                  sa.ForeignKey('companies.id'),
                  nullable=False),
        sa.Column('location_id',
                  sa.Integer,
                  sa.ForeignKey('locations.id'),
                  nullable=False),
    )


def downgrade():
    """Drops the `jobs` table."""
    op.drop_table('jobs')
