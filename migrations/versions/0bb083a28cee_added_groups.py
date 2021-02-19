"""added groups

Revision ID: 0bb083a28cee
Revises: b1bc79f2725c
Create Date: 2021-02-08 12:58:12.174757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bb083a28cee'
down_revision = 'b1bc79f2725c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('group', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'group')
    # ### end Alembic commands ###