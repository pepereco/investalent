"""empty message

Revision ID: 50ed9a87c695
Revises: 785ddf333cb3
Create Date: 2020-07-28 10:34:33.246515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '50ed9a87c695'
down_revision = '785ddf333cb3'
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
