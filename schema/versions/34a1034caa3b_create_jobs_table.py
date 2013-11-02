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
        sa.Column('title', sa.Unicode(100), nullable=False),
        sa.Column('description', sa.UnicodeText, nullable=True),
        sa.Column('how_to_apply', sa.UnicodeText, nullable=True),
        sa.Column('job_type', sa.Integer, nullable=False),
        sa.Column('remote_work', sa.Boolean, nullable=False, default=False),
        sa.Column('company_id',
                  sa.Integer,
                  sa.ForeignKey('companies.id'),
                  nullable=False),
    )


def downgrade():
    """Drops the `jobs` table."""
    op.drop_table('jobs')
