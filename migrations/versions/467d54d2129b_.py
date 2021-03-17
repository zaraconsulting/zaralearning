"""empty message

Revision ID: 467d54d2129b
Revises: dd5cefabf099
Create Date: 2021-03-17 16:18:19.646770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '467d54d2129b'
down_revision = 'dd5cefabf099'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('video_thumbnail', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course', 'video_thumbnail')
    # ### end Alembic commands ###
