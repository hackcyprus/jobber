"""create categories table

Revision ID: 26e3340ce799
Revises: 34a1034caa3b
Create Date: 2013-11-02 10:46:23.617628

"""
from alembic import op
import sqlalchemy as sa
import json


revision = '26e3340ce799'
down_revision = '34a1034caa3b'

# Load categories fixture file.
# TODO: create an abstraction for this.
with open('schema/initial/categories.json') as fixture:
    categories = json.loads(fixture.read())


def upgrade():
    """Creates and populates the `categories` table."""
    columns = (
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Unicode(50), nullable=False),
        sa.Column('slug',
                  sa.Unicode(75),
                  nullable=False,
                  unique=True,
                  index=True)
    )
    op.create_table('categories', *columns)
    op.bulk_insert(sa.sql.table('categories', *columns), categories)


def downgrade():
    """Drops the `jobs` table."""
    op.drop_table('categories')
