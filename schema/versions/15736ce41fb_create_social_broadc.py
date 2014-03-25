"""create social broadcast table

Revision ID: 15736ce41fb
Revises: 4eed47ecfc80
Create Date: 2014-03-25 20:54:40.615390

"""
from alembic import op
import sqlalchemy as sa


revision = '15736ce41fb'
down_revision = '4eed47ecfc80'


def upgrade():
    """Creates the `social_broadcasts` table."""
    op.create_table(
        'social_broadcasts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('service', sa.Unicode(25), nullable=False),
        sa.Column('success', sa.Boolean, nullable=False, default=True),
        sa.Column('data', sa.UnicodeText, nullable=True),
        sa.Column('job_id', sa.Integer, sa.ForeignKey('jobs.id'), index=True),
        sa.Column('created', sa.DateTime(timezone=True)),
    )


def downgrade():
    """Drops the `social_broadcasts` table."""
    op.drop_table('social_broadcasts')
