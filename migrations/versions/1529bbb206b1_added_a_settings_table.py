"""Added a settings table

Revision ID: 1529bbb206b1
Revises: 8e2971077330
Create Date: 2022-06-14 20:34:00.866899

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1529bbb206b1'
down_revision = '8e2971077330'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_setting', sa.Integer(), nullable=True),
    sa.Column('season_start', sa.DateTime(), nullable=True),
    sa.Column('season_end', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('settings')
    # ### end Alembic commands ###
