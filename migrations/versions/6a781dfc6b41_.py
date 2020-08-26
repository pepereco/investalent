"""empty message

Revision ID: 6a781dfc6b41
Revises: e072f4e0d899
Create Date: 2020-06-14 19:59:10.824116

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6a781dfc6b41'
down_revision = 'e072f4e0d899'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('current_actions', sa.Integer(), nullable=True))
    op.drop_column('projects', 'available_actions')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('available_actions', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_column('projects', 'current_actions')
    # ### end Alembic commands ###