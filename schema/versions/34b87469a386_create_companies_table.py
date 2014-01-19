"""create companies table

Revision ID: 34b87469a386
Revises: None
Create Date: 2013-11-02 00:18:39.132173

"""
from alembic import op
import sqlalchemy as sa


revision = '34b87469a386'
down_revision = None


def upgrade():
    """Creates the `companies` table."""
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime(timezone=True)),
        sa.Column('website', sa.Unicode(200), nullable=True),
        sa.Column('name', sa.Unicode(75), nullable=False),
        sa.Column('slug', sa.Unicode(125), nullable=False, unique=False),
    )


def downgrade():
    """Drops the `companies` table."""
    op.drop_table('companies')
