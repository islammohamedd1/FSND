"""empty message

Revision ID: 55e22c845060
Revises: 155cf843c6e0
Create Date: 2020-08-12 21:47:37.104776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55e22c845060'
down_revision = '155cf843c6e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'always_available',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'always_available',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
