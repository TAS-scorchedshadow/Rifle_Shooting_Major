"""finalised structure for settings

Revision ID: 50bbe0accd3c
Revises: d97e7d1fdcfc
Create Date: 2021-05-08 10:11:03.073426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50bbe0accd3c'
down_revision = 'd97e7d1fdcfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('rifle_buttHeight', sa.String(length=10), nullable=True))
    op.add_column('user', sa.Column('rifle_buttLength', sa.String(length=10), nullable=True))
    op.add_column('user', sa.Column('rifle_serial', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('rifle_sightHole', sa.String(length=10), nullable=True))
    op.add_column('user', sa.Column('rifle_slingPointLength', sa.String(length=10), nullable=True))
    op.drop_column('user', 'PPU300m')
    op.drop_column('user', 'Fore600m')
    op.drop_column('user', 'Fore400m')
    op.drop_column('user', 'Fore800m')
    op.drop_column('user', 'ADI500y')
    op.drop_column('user', 'hat')
    op.drop_column('user', 'ADI700m')
    op.drop_column('user', 'slingHole')
    op.drop_column('user', 'Fore700m')
    op.drop_column('user', 'Fore300m')
    op.drop_column('user', 'ADI400m')
    op.drop_column('user', 'butOut')
    op.drop_column('user', 'glove')
    op.drop_column('user', 'PPU600m')
    op.drop_column('user', 'ADI600m')
    op.drop_column('user', 'butUp')
    op.drop_column('user', 'sightHole')
    op.drop_column('user', 'jacket')
    op.drop_column('user', 'Fore500y')
    op.drop_column('user', 'slingPoint')
    op.drop_column('user', 'rifleSerial')
    op.drop_column('user', 'PPU500m')
    op.drop_column('user', 'ADI600y')
    op.drop_column('user', 'PPU800m')
    op.drop_column('user', 'PPU500y')
    op.drop_column('user', 'Fore500m')
    op.drop_column('user', 'PPU700m')
    op.drop_column('user', 'PPU400m')
    op.drop_column('user', 'ADI800m')
    op.drop_column('user', 'ADI500m')
    op.drop_column('user', 'PPU600y')
    op.drop_column('user', 'Fore600y')
    op.drop_column('user', 'ADI300m')
    op.drop_column('user', 'ringSize')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('ringSize', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI300m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore600y', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU600y', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI500m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI800m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU400m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU700m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore500m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU500y', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU800m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI600y', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU500m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('rifleSerial', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('slingPoint', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore500y', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('jacket', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('sightHole', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('butUp', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI600m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU600m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('glove', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('butOut', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI400m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore300m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore700m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('slingHole', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI700m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('hat', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('ADI500y', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore800m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore400m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('Fore600m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('PPU300m', sa.VARCHAR(length=8), autoincrement=False, nullable=True))
    op.drop_column('user', 'rifle_slingPointLength')
    op.drop_column('user', 'rifle_sightHole')
    op.drop_column('user', 'rifle_serial')
    op.drop_column('user', 'rifle_buttLength')
    op.drop_column('user', 'rifle_buttHeight')
    # ### end Alembic commands ###
