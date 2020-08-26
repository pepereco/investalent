"""empty message

Revision ID: 95f0f4e663a4
Revises: c6ab1eea3ce8
Create Date: 2020-08-20 13:05:05.471302

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '95f0f4e663a4'
down_revision = 'c6ab1eea3ce8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profiles', 'mark')
    op.drop_column('projects', 'available_actions')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('projects', sa.Column('available_actions', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('profiles', sa.Column('mark', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    # ### end Alembic commands ###