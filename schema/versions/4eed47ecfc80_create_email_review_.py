"""create email review tokens table

Revision ID: 4eed47ecfc80
Revises: 21a3732ed015
Create Date: 2014-02-17 22:44:21.386546

"""
from alembic import op
import sqlalchemy as sa


revision = '4eed47ecfc80'
down_revision = '21a3732ed015'


def upgrade():
    op.create_table(
        'email_review_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime(timezone=True)),
        sa.Column('token', sa.DateTime(timezone=True), unique=True, index=True),
        sa.Column('used', sa.Boolean, nullable=False, default=False),
        sa.Column('used_at', sa.DateTime(timezone=True)),
        sa.Column('job_id',
                  sa.Integer,
                  sa.ForeignKey('jobs.id'),
                  nullable=False),
    )


def downgrade():
    op.drop_table('email_review_tokens')

