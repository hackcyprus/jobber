"""create admin tokens table

Revision ID: 1443b2a70265
Revises: 468946541a57
Create Date: 2013-11-24 22:21:05.614906

"""
from alembic import op
import sqlalchemy as sa


revision = '1443b2a70265'
down_revision = '468946541a57'


def upgrade():
    """Creates the `admin_tokens` table."""
    op.create_table(
        'admin_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime(timezone=True)),
        sa.Column('token', sa.String(40), nullable=False),
        sa.Column('job_id', sa.Integer, nullable=False)
    )


def downgrade():
    """Drops the `admin_tokens` table."""
    op.drop_table('admin_tokens')
