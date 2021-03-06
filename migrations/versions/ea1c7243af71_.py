"""empty message

Revision ID: ea1c7243af71
Revises: 718ec7aeb1a0
Create Date: 2021-03-28 12:56:41.157366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea1c7243af71'
down_revision = '718ec7aeb1a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course_review', sa.Column('name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course_review', 'name')
    # ### end Alembic commands ###
