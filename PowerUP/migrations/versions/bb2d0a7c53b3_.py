"""empty message

Revision ID: bb2d0a7c53b3
Revises: af1cabc2b52b
Create Date: 2021-02-11 00:14:03.721569

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bb2d0a7c53b3'
down_revision = 'af1cabc2b52b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('device', 'pictures',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('device', 'pictures',
               existing_type=mysql.TEXT(collation='utf8_unicode_ci'),
               nullable=False)
    # ### end Alembic commands ###
