"""create locations table

Revision ID: 468946541a57
Revises: 26e3340ce799
Create Date: 2013-11-03 23:24:23.069426

"""
from alembic import op
import sqlalchemy as sa


revision = '468946541a57'
down_revision = '26e3340ce799'


def upgrade():
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created', sa.DateTime(timezone=True)),
        sa.Column('city', sa.Unicode(75), nullable=False),
        sa.Column('country', sa.Unicode(50), nullable=False)
    )

def downgrade():
    op.drop_table('locations')
