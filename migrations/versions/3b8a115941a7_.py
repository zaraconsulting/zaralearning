"""empty message

Revision ID: 3b8a115941a7
Revises: b201019b6302
Create Date: 2021-03-16 12:57:57.660058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b8a115941a7'
down_revision = 'b201019b6302'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('customer_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'account', ['customer_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'account', type_='unique')
    op.drop_column('account', 'customer_id')
    # ### end Alembic commands ###
