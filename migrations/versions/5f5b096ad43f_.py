"""empty message

Revision ID: 5f5b096ad43f
Revises: ffad193b06f1
Create Date: 2021-01-30 14:30:09.716943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f5b096ad43f'
down_revision = 'ffad193b06f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'role', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'role', type_='unique')
    # ### end Alembic commands ###
