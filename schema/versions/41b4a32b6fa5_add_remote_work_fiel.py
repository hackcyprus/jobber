"""add remote_work field in jobs table

Revision ID: 41b4a32b6fa5
Revises: 34a1034caa3b
Create Date: 2013-11-02 03:23:01.176449

"""
from alembic import op
import sqlalchemy as sa


revision = '41b4a32b6fa5'
down_revision = '34a1034caa3b'


def upgrade():
    op.add_column('jobs', sa.Column('remote_work',
                                    sa.Boolean,
                                    default=False,
                                    nullable=False))


def downgrade():
    op.drop_column('jobs', 'remote_work')
