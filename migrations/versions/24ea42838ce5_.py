"""empty message

Revision ID: 24ea42838ce5
Revises: e076199d4601
Create Date: 2021-03-21 01:21:16.793492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24ea42838ce5'
down_revision = 'e076199d4601'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course_category', sa.Column('slug', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course_category', 'slug')
    # ### end Alembic commands ###
